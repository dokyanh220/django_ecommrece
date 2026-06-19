from django.shortcuts import render, redirect
from app.models import Account
from django.db.models import Q
from django.contrib.auth.hashers import make_password
import csv
from django.http import HttpResponse
from django.contrib import messages

def check_admin(request):
    return request.session.get('role') == 'ADMIN'

def account_export(request):
    if not check_admin(request):
        return redirect('home')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="accounts.csv"'
    
    # Write UTF-8 BOM
    response.write(b'\xef\xbb\xbf')

    writer = csv.writer(response)
    writer.writerow(['Họ và tên', 'Tên đăng nhập', 'Email', 'Vai trò', 'Trạng thái'])

    accounts = Account.objects.all()
    for acc in accounts:
        status_str = 'Hoạt động' if acc.status else 'Bị khóa'
        writer.writerow([acc.fullname, acc.username, acc.email, acc.role, status_str])

    return response

def account_import(request):
    if not check_admin(request):
        return redirect('home')

    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file:
            messages.error(request, 'Vui lòng chọn file CSV để nhập.')
            return redirect('account_list')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File không đúng định dạng .csv')
            return redirect('account_list')

        try:
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.reader(decoded_file)
            
            # Skip header
            try:
                next(reader)
            except StopIteration:
                messages.error(request, 'File CSV trống')
                return redirect('account_list')

            success_count = 0
            update_count = 0
            skipped_count = 0

            for row in reader:
                if not row or len(row) < 3:
                    continue
                
                fullname = row[0].strip()
                username = row[1].strip()
                email = row[2].strip()
                password = row[3].strip() if len(row) > 3 else ''
                role = row[4].strip().upper() if len(row) > 4 else 'USER'
                
                # Default status to True unless explicitly locked/false
                status = True
                if len(row) > 5:
                    status_raw = row[5].strip().lower()
                    if status_raw in ('false', '0', 'bị khóa', 'locked'):
                        status = False

                if not username or not email:
                    skipped_count += 1
                    continue

                try:
                    account = Account.objects.get(username=username)
                    # Check if email is already taken by another account
                    if Account.objects.exclude(id=account.id).filter(email=email).exists():
                        skipped_count += 1
                        continue
                    
                    account.fullname = fullname
                    account.email = email
                    if password:
                        account.password = make_password(password)
                    if role in ('ADMIN', 'USER'):
                        account.role = role
                    account.status = status
                    account.save()
                    
                    # Update active session if editing own account
                    if str(account.id) == str(request.session.get('account_id')):
                        request.session['fullname'] = account.fullname
                        request.session['username'] = account.username
                        request.session['avatar'] = account.avatar.url if account.avatar else ''
                        request.session.modified = True
                        
                    update_count += 1
                except Account.DoesNotExist:
                    # Check if email is already taken
                    if Account.objects.filter(email=email).exists():
                        skipped_count += 1
                        continue
                    
                    hashed_password = make_password(password if password else '123456')
                    Account.objects.create(
                        fullname=fullname,
                        username=username,
                        email=email,
                        password=hashed_password,
                        role=role if role in ('ADMIN', 'USER') else 'USER',
                        status=status,
                        is_verified=True
                    )
                    success_count += 1

            messages.success(request, f'Nhập thành công! Thêm mới: {success_count}, Cập nhật: {update_count}, Bỏ qua: {skipped_count}')
        except Exception as e:
            messages.error(request, f'Lỗi đọc file CSV: {str(e)}')

    return redirect('account_list')

def account_list(request):
    if not check_admin(request):
        return redirect('home')

    keyword = request.GET.get('keyword', '')
    accounts = Account.objects.all()

    if keyword:
        accounts = accounts.filter(
            Q(fullname__icontains=keyword) | 
            Q(username__icontains=keyword) | 
            Q(email__icontains=keyword)
        )

    return render(request, 'account/list.html', {
        'accounts': accounts,
        'keyword': keyword
    })

def account_create(request):
    if not check_admin(request):
        return redirect('home')

    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        status = request.POST.get('status') == 'True'
        avatar = request.FILES.get('avatar')

        if Account.objects.filter(username=username).exists():
            return render(request, 'account/create.html', {'error': 'Tên đăng nhập đã tồn tại'})
        
        if Account.objects.filter(email=email).exists():
            return render(request, 'account/create.html', {'error': 'Email đã tồn tại'})

        Account.objects.create(
            fullname=fullname,
            username=username,
            email=email,
            password=password,
            role='USER',
            status=status,
            avatar=avatar
        )
        return redirect('account_list')

    return render(request, 'account/create.html')

def account_edit(request, id):
    if not check_admin(request):
        return redirect('home')

    try:
        account = Account.objects.get(id=id)
    except Account.DoesNotExist:
        return redirect('account_list')

    current_account_id = str(request.session.get('account_id'))
    if account.role == 'ADMIN' and str(account.id) != current_account_id:
        return redirect('account_list')
    
    if request.method == 'POST':
        account.fullname = request.POST.get('fullname')
        
        new_email = request.POST.get('email')
        if new_email != account.email and Account.objects.filter(email=new_email).exists():
            return render(request, 'account/edit.html', {'account': account, 'error': 'Email đã tồn tại'})
        account.email = new_email

        new_password = request.POST.get('password')
        if new_password:
            account.password = new_password

        account.status = request.POST.get('status') == 'True'
        
        avatar = request.FILES.get('avatar')
        if avatar:
            account.avatar = avatar
            
        account.save()

        # Update session if editing own account
        if str(account.id) == str(request.session.get('account_id')):
            request.session['fullname'] = account.fullname
            request.session['username'] = account.username
            request.session['avatar'] = account.avatar.url if account.avatar else ''
            request.session.modified = True

        return redirect('account_list')

    return render(request, 'account/edit.html', {'account': account})

def account_delete(request, id):
    if not check_admin(request):
        return redirect('home')

    if str(request.session.get('account_id')) == str(id):
        return redirect('account_list')
    try:
        account = Account.objects.get(id=id)
    except Account.DoesNotExist:
        return redirect('account_list')
    
    current_account_id = str(request.session.get('account_id'))
    if account.role == 'ADMIN' and str(account.id) != current_account_id:
        return redirect('account_list')
    
    account.delete()

    return redirect('account_list')

def account_toggle_status(request, id):
    if not check_admin(request):
        return redirect('home')

    if str(request.session.get('account_id')) == str(id):
        return redirect('account_list')
    
    try:
        account = Account.objects.get(id=id)
    except Account.DoesNotExist:
        return redirect('account_list')
        
    current_account_id = str(request.session.get('account_id'))
    if account.role == 'ADMIN' and str(account.id) != current_account_id:
        messages.error(request, 'Bạn không có quyền chỉnh sửa thông tin của Admin khác.')
        return redirect('account_list')
    
    account.status = not account.status
    account.save()
    return redirect('account_list')

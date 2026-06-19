from django.shortcuts import render, redirect
from app.models import Account
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            return render(request, 'auth/login.html', {'error': 'Vui lòng nhập đầy đủ thông tin'})
        try:
            account = Account.objects.get(username=username)

            if not check_password(password, account.password):
                return render(request, 'auth/login.html', {'error': 'Sai tài khoản hoặc mật khẩu'})
            
            if not account.status:
                return render(request, 'auth/login.html', {'error': 'Tài khoản bị khóa'})

            if not account.is_verified:
                return render(request, 'auth/login.html', {'error': 'Tài khoản chưa xác thực email. Vui lòng kiểm tra email để xác thực.'})
            
            request.session.flush()

            request.session['account_id'] = account.id
            request.session['role'] = account.role
            request.session['username'] = account.username
            request.session['fullname'] = account.fullname
            request.session['avatar'] = account.avatar.url if account.avatar else ''

            return redirect('home')
        except Account.DoesNotExist:
            return render(request, 'auth/login.html', {'error': 'Tài khoản không tồn tại'})
        except Exception as e:
            return render(request, 'auth/login.html', {'error': 'Lỗi hệ thống'})
    return render(request, 'auth/login.html')

def register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not fullname or not username or not email or not password:
            return render(request, 'auth/register.html', { 'error': 'Vui lòng điền đầy đủ thông tin' })

        if Account.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', { 'error': 'Tên đăng nhập đã tồn tại' })
        if Account.objects.filter(email=email).exists():
            return render(request, 'auth/register.html', { 'error': 'Email đã tồn tại' })
        
        try:
            account = Account.objects.create(
                fullname=fullname,
                username=username,
                email=email,
                password=make_password(password),
                role='USER',
                is_verified=False
            )
            
            # Gửi email xác thực
            signer = TimestampSigner()
            token = signer.sign_object({'username': username})
            scheme = 'https' if request.is_secure() else 'http'
            verify_url = f"{scheme}://{request.get_host()}{reverse('verify_email', args=[token])}"
            
            subject = 'Xác thực tài khoản của bạn'
            message = f'Chào {fullname},\n\nCảm ơn bạn đã đăng ký tài khoản. Vui lòng click vào link dưới đây để xác thực tài khoản:\n{verify_url}\n\nLink xác thực có hiệu lực trong vòng 24 giờ.'
            
            html_message = f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                <h2 style="color: #4f46e5; text-align: center;">Xác Thực Tài Khoản</h2>
                <p>Chào <strong>{fullname}</strong>,</p>
                <p>Cảm ơn bạn đã đăng ký tài khoản tại hệ thống của chúng tôi. Vui lòng nhấn vào nút bên dưới để xác thực địa chỉ email và kích hoạt tài khoản của bạn:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verify_url}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Kích hoạt tài khoản</a>
                </div>
                <p style="color: #666; font-size: 14px;">Nếu nút trên không hoạt động, bạn có thể sao chép và dán liên kết này vào trình duyệt của mình:</p>
                <p style="color: #4f46e5; word-break: break-all; font-size: 14px;">{verify_url}</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">Liên kết này sẽ hết hạn trong vòng 24 giờ. Nếu bạn không thực hiện đăng ký này, vui lòng bỏ qua email này.</p>
            </div>
            '''
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return render(request, 'auth/login.html', {
                'success': 'Đăng ký thành công! Một email xác thực đã được gửi tới địa chỉ của bạn. Vui lòng kiểm tra và kích hoạt tài khoản trước khi đăng nhập.'
            })
        except Exception as e:
            return render(request, 'auth/register.html', { 'error': f'Lỗi hệ thống khi gửi email: {str(e)}' })
    
    return render(request, 'auth/register.html')

def logout(request):
    request.session.flush()
    return redirect('home')

def profile(request):
    account_id = request.session.get('account_id')
    if not account_id:
        return redirect('login')

    try:
        account = Account.objects.get(id=account_id)
    except Account.DoesNotExist:
        request.session.flush()
        return redirect('login')
    
    context = {'account': account}

    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        email = request.POST.get('email', '').strip()
        avatar = request.FILES.get('avatar')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not fullname:
            context['error'] = 'Họ và tên không được để trống'
            return render(request, 'auth/profile.html', context)

        if not email:
            context['error'] = 'Email không được để trống'
            return render(request, 'auth/profile.html', context)

        if Account.objects.exclude(id=account.id).filter(email=email).exists():
            context['error'] = 'Email đã tồn tại'
            return render(request, 'auth/profile.html', context)

        if old_password or new_password or confirm_password:
            if not old_password or not new_password or not confirm_password:
                context['error'] = 'Vui lòng điền đầy đủ thông tin'
                return render(request, 'auth/profile.html', context)
            
            if not check_password(old_password, account.password):
                context['error'] = 'Mật khẩu tài khoản sai'
                return render(request, 'auth/profile.html', context)
            
            if len(new_password) < 6:
                context['error'] = 'Mật khẩu mới phải có ít nhất 6 ký tự.'
                return render(request, 'auth/profile.html', context)
            
            account.password = make_password(new_password)

        account.fullname = fullname
        account.email = email
        if avatar:
            account.avatar = avatar
        
        try:
            account.save()
            context['success'] = 'Cập nhật hồ sơ thành công'

            request.session['username'] = account.username
            request.session['fullname'] = account.fullname
            request.session['avatar'] = account.avatar.url if account.avatar else ''

            request.session.modified = True
        except Exception as e:
            context['error'] = 'Lỗi hệ thống'
    return render(request, 'auth/profile.html', context)

def verify_email(request, token):
    signer = TimestampSigner()
    try:
        data = signer.unsign_object(token, max_age=86400) # 24 hours
        username = data.get('username')
        account = Account.objects.get(username=username)
        if not account.is_verified:
            account.is_verified = True
            account.save()
            return render(request, 'auth/login.html', {'success': 'Xác thực tài khoản thành công! Bạn có thể đăng nhập ngay.'})
        else:
            return render(request, 'auth/login.html', {'success': 'Tài khoản của bạn đã được xác thực trước đó.'})
    except (BadSignature, SignatureExpired, Account.DoesNotExist) as e:
        return render(request, 'auth/login.html', {'error': 'Liên kết xác thực không hợp lệ hoặc đã hết hạn.'})

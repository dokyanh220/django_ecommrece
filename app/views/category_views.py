from django.shortcuts import render, redirect
from app.models import Category
import csv
from django.http import HttpResponse
from django.contrib import messages

def category_export(request):
    if request.session.get('role') != 'ADMIN':
        return redirect('home')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="categories.csv"'
    
    # Write UTF-8 BOM
    response.write(b'\xef\xbb\xbf')

    writer = csv.writer(response)
    writer.writerow(['Tên danh mục', 'Mô tả'])

    categories = Category.objects.all()
    for cat in categories:
        writer.writerow([cat.name, cat.description or ''])

    return response

def category_import(request):
    if request.session.get('role') != 'ADMIN':
        return redirect('home')

    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file:
            messages.error(request, 'Vui lòng chọn file CSV để nhập.')
            return redirect('category_list')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File không đúng định dạng .csv')
            return redirect('category_list')

        try:
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.reader(decoded_file)
            
            # Skip header
            try:
                next(reader)
            except StopIteration:
                messages.error(request, 'File CSV trống')
                return redirect('category_list')

            success_count = 0
            update_count = 0

            for row in reader:
                if not row or len(row) < 1:
                    continue
                
                name = row[0].strip()
                description = row[1].strip() if len(row) > 1 else ''

                if not name:
                    continue

                category, created = Category.objects.get_or_create(
                    name=name,
                    defaults={'description': description}
                )
                if not created:
                    category.description = description
                    category.save()
                    update_count += 1
                else:
                    success_count += 1

            messages.success(request, f'Nhập thành công! Thêm mới: {success_count}, Cập nhật: {update_count}')
        except Exception as e:
            messages.error(request, f'Lỗi đọc file CSV: {str(e)}')

    return redirect('category_list')

def category_list(request):
    keyword = request.GET.get('keyword', '')
    categories = Category.objects.all()
    if keyword:
        categories = categories.filter(name__icontains=keyword)

    return render(request, 'category/list.html', {
        'categories': categories,
        'keyword': keyword
    })

def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if Category.objects.filter(name=name).exists():
            return render(request, 'category/create.html', {'error': 'Danh mục đã tồn tại'})

        Category.objects.create(
            name=name,
            description=request.POST.get('description'),
            image=request.FILES.get('image')
        )
        return redirect('category_list')

    return render(request, 'category/create.html')

def category_edit(request, id):
    category = Category.objects.get(id=id)

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        image = request.FILES.get('image')
        if image:
            category.image = image
        category.save()
        
        return redirect('category_list')

    return render(request, 'category/edit.html', {'category': category})

def category_delete(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    return redirect('category_list')

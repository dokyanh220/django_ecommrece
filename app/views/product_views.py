from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from app.models import Product, Category, ProductImage
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse
from django.contrib import messages
from decimal import Decimal

def product_list(request):
    keyword = request.GET.get('keyword', '')
    category_id = request.GET.get('category_id', '')
    sort = request.GET.get('sort', '')

    products = Product.objects.select_related('category')
    if keyword:
        products = products.filter(name__icontains=keyword)
    if category_id:
        products = products.filter(category_id=category_id)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    categories = Category.objects.all()

    # Pagination: 8 products per page
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Rebuild query params string (except 'page') to preserve filters in pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()
    
    return render(request, 'product/list.html', {
        'products': page_obj.object_list, # backward compatibility
        'page_obj': page_obj,
        'query_string': query_string,
        'categories': categories,
        'keyword': keyword,
        'category_id': category_id,
        'sort': sort
    })

def product_export(request):
    if request.session.get('role') != 'ADMIN':
        return redirect('home')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    
    # Write UTF-8 BOM
    response.write(b'\xef\xbb\xbf')

    writer = csv.writer(response)
    writer.writerow(['Danh mục', 'Tên sản phẩm', 'Mô tả', 'Giá', 'Số lượng', 'Trạng thái'])

    products = Product.objects.select_related('category').all()
    for prod in products:
        status_str = 'Hiển thị' if prod.status else 'Ẩn'
        cat_name = prod.category.name if prod.category else ''
        writer.writerow([cat_name, prod.name, prod.description or '', int(prod.price), prod.quantity, status_str])

    return response

def product_import(request):
    if request.session.get('role') != 'ADMIN':
        return redirect('home')

    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file:
            messages.error(request, 'Vui lòng chọn file CSV để nhập.')
            return redirect('product_list')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File không đúng định dạng .csv')
            return redirect('product_list')

        try:
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.reader(decoded_file)
            
            # Skip header
            try:
                next(reader)
            except StopIteration:
                messages.error(request, 'File CSV trống')
                return redirect('product_list')

            success_count = 0
            update_count = 0
            skipped_count = 0

            for row in reader:
                if not row or len(row) < 4:
                    continue
                
                cat_name = row[0].strip()
                name = row[1].strip()
                description = row[2].strip()
                
                try:
                    price = Decimal(row[3].strip())
                except (ValueError, IndexError):
                    price = Decimal('0')

                try:
                    quantity = int(row[4].strip()) if len(row) > 4 else 0
                except ValueError:
                    quantity = 0

                status = True
                if len(row) > 5:
                    status_raw = row[5].strip().lower()
                    if status_raw in ('false', '0', 'ẩn', 'hidden', 'off'):
                        status = False

                if not name or not cat_name:
                    skipped_count += 1
                    continue

                # Get or create Category
                category, _ = Category.objects.get_or_create(name=cat_name)

                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'description': description,
                        'price': price,
                        'quantity': quantity,
                        'status': status
                    }
                )
                
                if not created:
                    product.category = category
                    product.description = description
                    product.price = price
                    product.quantity = quantity
                    product.status = status
                    product.save()
                    update_count += 1
                else:
                    success_count += 1

            messages.success(request, f'Nhập thành công! Thêm mới: {success_count}, Cập nhật: {update_count}, Bỏ qua: {skipped_count}')
        except Exception as e:
            messages.error(request, f'Lỗi đọc file CSV: {str(e)}')

    return redirect('product_list')

def product_detail(request, id):
    product = Product.objects.select_related('category').get(id=id)
    images = product.images.all()
    # Fetch 4 random products from the same category for "Related Products"
    related_products = list(Product.objects.filter(category=product.category, status=True).exclude(id=product.id).order_by('?')[:4])
    if len(related_products) < 4:
        needed = 4 - len(related_products)
        excluded_ids = [product.id] + [p.id for p in related_products]
        extras = Product.objects.filter(status=True).exclude(id__in=excluded_ids).order_by('?')[:needed]
        related_products.extend(list(extras))
    return render(request, 'product/detail.html', {
        'product': product, 
        'images': images, 
        'related_products': related_products
    })

def product_create(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category_id')

        if Product.objects.filter(name=name).exists():
            return render(request, 'product/create.html', {'error': 'Sản phẩm đã tồn tại', 'categories': categories})
        if not category_id:
            return render(request, 'product/create.html', {'error': 'Vui lòng chọn danh mục', 'categories': categories})

        try:
            quantity = int(request.POST.get('quantity', 0))
            price = Decimal(request.POST.get('price', 0))
        except (ValueError, TypeError):
            return render(request, 'product/create.html', {'error': 'Số lượng hoặc giá không hợp lệ', 'categories': categories})
        
        status_val = request.POST.get('status') == 'active'

        product = Product.objects.create(
            category_id=category_id,
            name=name,
            description=request.POST.get('description'),
            price=price,
            quantity=quantity,
            image=request.FILES.get('image'),
            status=status_val
        )
        
        gallery_images = request.FILES.getlist('images')
        for img in gallery_images:
            ProductImage.objects.create(product=product, image=img)
            
        return redirect('product_list')

    return render(request, 'product/create.html', {'categories': categories})

def product_edit(request, id):
    try:
        product = Product.objects.select_related('category').get(id=id)
    except Product.DoesNotExist:
        return redirect('product_list')
    
    categories = Category.objects.all()

    if request.method == 'POST':
        product.category_id = request.POST.get('category_id')
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')

        try:
            product.price = Decimal(request.POST.get('price', 0))
            product.quantity = int(request.POST.get('quantity', 0))
        except (ValueError, TypeError):
            return render(request, 'product/edit.html', {'product': product, 'error': 'Dữ liệu không hợp lệ'})
        
        product.status = request.POST.get('status') == 'active'

        image = request.FILES.get('image')
        if image:
            product.image = image
            
        try:
            product.save()
            
            # Handle new gallery images
            gallery_images = request.FILES.getlist('images')
            for img in gallery_images:
                ProductImage.objects.create(product=product, image=img)
                
        except ValidationError as e:
            return render(request, 'product/edit.html', {
                'product': product, 
                'error': str(e)
            })

        return redirect('product_list')

    return render(request, 'product/edit.html', {
        'product': product,
        'categories': categories
    })

def product_delete(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('product_list')

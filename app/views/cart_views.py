import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from app.models import CartItem, Product

def cart(request):
    account_id = request.session.get('account_id')
    if not account_id:
        return redirect('login')

    try:
        cart_items = CartItem.objects.filter(account_id=account_id).select_related('product')
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        
        return render(request, 'product/cart.html', {
            'cart_items': cart_items,
            'total_price': total_price
        })
    except Exception as e:
        return render(request, 'product/cart.html', {
            'cart_items': [],
            'total_price': 0,
            'error': 'Đã xảy ra lỗi khi tải giỏ hàng.'
        })

@require_http_methods(["POST"])
@transaction.atomic
def update_cart_api(request):
    account_id = request.session.get('account_id')
    if not account_id:
        return JsonResponse({'error': 'Vui lòng đăng nhập'}, status=401)

    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = data.get('quantity')

        if not item_id or not isinstance(quantity, int):
            return JsonResponse({'error': 'Dữ liệu không hợp lệ'}, status=400)

        cart_item = CartItem.objects.select_for_update().get(id=item_id, account_id=account_id)
        
        if quantity > cart_item.product.quantity:
            return JsonResponse({'error': 'Số lượng yêu cầu vượt quá tồn kho hiện tại.'}, status=400)
            
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        return JsonResponse({'success': True, 'message': 'Đã cập nhật giỏ hàng'})
        
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Sản phẩm không tồn tại trong giỏ hàng.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Sai định dạng JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Lỗi hệ thống'}, status=500)

@transaction.atomic
def add_to_cart(request):
    if request.method != 'POST':
        return redirect('home')

    account_id = request.session.get('account_id')
    if not account_id:
        return redirect('login')

    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    buy_now = request.POST.get('buy_now') == 'true'

    if quantity < 1:
        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)

    try:
        product = Product.objects.get(id=product_id, status=True)
        
        cart_item, created = CartItem.objects.get_or_create(
            account_id=account_id,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity <= product.quantity:
                cart_item.quantity = new_quantity
                cart_item.save()

    except ObjectDoesNotExist:
        pass

    if buy_now:
        return redirect('checkout')

    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)

def checkout(request):
    account_id = request.session.get('account_id')
    if not account_id:
        return redirect('login')
        
    cart_items = CartItem.objects.filter(account_id=account_id).select_related('product')
    if not cart_items:
        return redirect('cart')
        
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'product/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@require_http_methods(["POST"])
@transaction.atomic
def checkout_process(request):
    account_id = request.session.get('account_id')
    if not account_id:
        return redirect('login')
        
    # Fake processing
    # Delete cart items
    CartItem.objects.filter(account_id=account_id).delete()
    return redirect('checkout_success')

def checkout_success(request):
    return render(request, 'product/checkout_success.html')

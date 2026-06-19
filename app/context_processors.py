from app.models import CartItem

def cart_processor(request):
    cart_count = 0
    account_id = request.session.get('account_id')
    if account_id:
        cart_items = CartItem.objects.filter(account_id=account_id)
        cart_count = sum(item.quantity for item in cart_items)
    return {'cart_count': cart_count}

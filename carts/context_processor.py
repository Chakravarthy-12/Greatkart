from carts.views import _cart_id
from .models import Cart, CartItem  

def count_cart_items(request):
    cart_item_count = 0
    if 'admin' in request.path:
        return {}
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
        for cart_item in cart_items:
            cart_item_count += cart_item.quantity
    except Cart.DoesNotExist: 
        cart_item_count = 0
    return dict(cart_item_count=cart_item_count)
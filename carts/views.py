from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from store.models import Variation
from .models import Product,Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key=item
            value=request.POST[key] 
            
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                print(variation)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass
        
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        existing_variation_list = []
        for item in cart_item:
            existing_variation_list.append(list(item.variation.all()))
            print(f"existing_variation_list: {existing_variation_list}")

        if product_variation in existing_variation_list:
            index = existing_variation_list.index(product_variation)
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item[index].id)
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            print(f"cart_item: {cart_item}")
            if len(product_variation) > 0:
                cart_item.variation.clear()
                print(f"product_variation: {product_variation}")
                cart_item.variation.add(*product_variation)
            cart_item.save()
    else:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        if len(product_variation) > 0:
            cart_item.variation.clear()
            print(f"product_variation: {product_variation}")
            cart_item.variation.add(*product_variation)

        cart_item.save()
    
    return redirect('cart')

def remove_from_cart(request, product_id,cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except ObjectDoesNotExist:
        pass
    return redirect('cart')

# delete the product(cart item) from the cart
def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except ObjectDoesNotExist:
        pass
    return redirect('cart')

def cart(request,total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = round((total * 2) / 100, 2)
        grand_total = round(total + tax, 2)
    except ObjectDoesNotExist:
        pass
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html',context=context)
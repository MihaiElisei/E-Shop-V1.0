from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .models import Cart, CartItem
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


def view_cart(request, total=0, quantity=0, cart_items=None):
    """ A view that renders the cart contents page,
        display all items from the cart 
        and calculates the grand total for the cart
    """
    try:
        vat = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        vat = total / 100  # Set VAT at 1%

        if total < settings.FREE_DELIVERY_THRESHOLD:
            delivery = settings.STANDARD_DELIVERY_PRICE
            free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
        else:
            delivery = 0
            free_delivery_delta = 0

        grand_total = delivery + total + vat
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'vat': vat,
        'grand_total': grand_total,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
    }
    return render(request, 'cart/cart.html', context)


def _cart_id(request):
    """ A private function to get the cart id from the current session or create a new session """

    cart = request.session.session_key  # Get the session id
    if not cart:
        # Create a new session if there is no session available
        cart = request.session.create()
    return cart


def add_to_cart(request, product_id):
    """ A view that manages add items to the cart """

    product = Product.objects.get(id=product_id)
    try:
        # get the cart using the cart id present in the session
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            # Create a new cart if there is no cart session created
            cart_id=_cart_id(request),
        )
    cart.save()

    # put the product inside the cart
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1  # Increment the quantity of the item inside the cart
        cart_item.save()
    except CartItem.DoesNotExist:  # Create a new cart item if there is no cart item in the cart
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        cart_item.save()
    return redirect('view_cart')


def remove_from_cart(request, product_id):
    """ A view to remove items from the cart """

    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(
            product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(
                request, f'Removed {product.name} from your cart!')

        else:
            cart_item.delete()
            messages.success(
                request, f'Removed {product.name} from your cart!')
    except Exception as e:
        messages.success(request, f'Error removing item: {e} from your cart!')
    return redirect('view_cart')


def remove_cart_item(request, product_id):
    """ A view to remove items from the cart """

    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    cart_item.delete()
    messages.success(request, f'Removed {product.name} from your cart!')
    return redirect('view_cart')

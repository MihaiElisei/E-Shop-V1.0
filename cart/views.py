from django.shortcuts import render, redirect
from products.models import Product
from .models import Cart, CartItem
# Create your views here.


def view_cart(request):
    """ A view that renders the cart contents page """

    return render(request, 'cart/cart.html')


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

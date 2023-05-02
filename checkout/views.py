from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from .forms import OrderForm
from products.models import Product
from .models import OrderLineItem, Order
from cart.models import Cart, CartItem
from cart.views import _cart_id
from cart.contexts import cart_contents
import stripe

# Create your views here.


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    cart = Cart.objects.get(cart_id=_cart_id(request))
    if not cart:
        messages.error(request, "There is nothing in your cart at the moment!")
        return redirect(reverse('/'))
    else:
        print(cart)
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': 'Test client secret',
    }

    return render(request, template, context)



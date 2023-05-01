from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm
from cart.models import Cart
from cart.views import _cart_id

# Create your views here.


def checkout(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        if not cart:
            messages.error(
                request, 'There`s nothing in your cart at the moment')
            return redirect(reverse('products'))
    except:
        pass
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form
    }

    return render(request, template, context)

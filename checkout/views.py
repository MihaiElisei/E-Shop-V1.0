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
    
    if request.method == 'POST':
        print('POST')
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.all()
        print(cart_items)
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save()
            for item in cart_items:
                print(item.product.name)
                try:
                    
                    order_line_item = OrderLineItem(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,

                    )
                except Product.DoesNotExist:
                    messages.error(request, "One of the products was not found!")
                    order.delete()
                    return redirect(reverse('view_cart'))
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
           messages.error(request, 'There was an error with the form')
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        current_cart = cart_contents(request)
        total = current_cart['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
        order_form = OrderForm()
        if not stripe_public_key:
            messages.warning(request, "Stripe public key is missing")

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    cart = Cart.objects.get(cart_id=_cart_id(request))
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')
    cart = Cart.objects.get(cart_id=_cart_id(request))
    
    
    
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)
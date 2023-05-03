from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from .forms import OrderForm
from products.models import Product
from .models import OrderLineItem, Order
from cart.models import Cart, CartItem
from cart.views import _cart_id
from cart.contexts import cart_contents
import stripe


@require_POST
def cache_checkout_data(request):
    try:
        cart = []
        cart_items = CartItem.objects.all()
        for item in cart_items:
            cart.append(item.product.name)
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': str(cart),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, ('Sorry, your payment cannot be '
                                 'processed right now. Please try '
                                 'again later.'))
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        cart_items = CartItem.objects.all()

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
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.save()
            for item in cart_items:
                product_variation = ''
                if item.variations.all():
                    product_variation_list = list(item.variations.all())
                    product_variation_value = product_variation_list[0]
                    product_variation_category = product_variation_list[1]
                    product_variation = f"Color:{product_variation_value} and Size: {product_variation_category}"
                else:
                    product_variation = 'No product variations at this time!'
                try:
                    order_line_item = OrderLineItem(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        product_variation=product_variation
                    )
                    order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(
                        request, "One of the products was not found!")
                    order.delete()
                    return redirect(reverse('view_cart'))
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with the form')
    else:
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
    cart_items = CartItem.objects.filter(cart=cart)
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items.delete()
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)

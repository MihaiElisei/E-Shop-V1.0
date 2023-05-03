from django.http import HttpResponse
from .models import Order, OrderLineItem
from cart.models import CartItem
import stripe
import time


class StripeWH_Handler:
    """ Handle Stripe webhools """

    def __init__(self, request):
        self.request = request
        print(request)

    def handle_event(self, event):
        """ Handle a generic/unknown webhook event """

        return HttpResponse(
            content=f'Unhandled received: {event["type"]}',
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        cart_items = CartItem.objects.all()
        intent = event.data.object
        pid = intent.id

        # Get the Charge object
        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )

        billing_details = stripe_charge.billing_details  # updated
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)  # updated

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    stripe_pid=pid,
                )
                print(order)
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            return HttpResponse(
                content=(f'Webhook received: {event["type"]} | SUCCESS: '
                         'Verified order already in database'),
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    stripe_pid=pid,
                )
                for item in cart_items:
                    product_variation = ''
                    if item.variations.all():
                        product_variation_list = list(item.variations.all())
                        product_variation_value = product_variation_list[0]
                        product_variation_category = product_variation_list[1]
                        product_variation = f"Color:{product_variation_value} and Size: {product_variation_category}"
                    else:
                        product_variation = 'No product variations at this time!'
                        order_line_item = OrderLineItem(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            product_variation=product_variation
                        )
                        order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        """ Handle the payment intent failed webhook from stripe """

        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200
        )

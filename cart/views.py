from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from products.models import Product, Variation
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
    """ A view that manages add items to the cart
        and products variation 
     """

    product = Product.objects.get(id=product_id)
    product_variation = []

    # Product Variations for colors and sizes
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)
            except:
                pass

    try:
        # get the cart using the cart id present in the session
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            # Create a new cart if there is no cart session created
            cart_id=_cart_id(request)
        )
    cart.save()

    if product_variation:
        messages.success(
            request, f'Added {product.name} with color {product_variation[0]} and size {product_variation[1]} to your cart')
    else:
        messages.success(request, f'Added {product.name} to your cart')
    cart_item_exists = CartItem.objects.filter(
        product=product, cart=cart).exists()

    if cart_item_exists:
        cart_item = CartItem.objects.filter(
            product=product,
            cart=cart
        )
        existing_variation_list = []
        id = []
        for item in cart_item:  # If the cart item exists loop the cart item and get variations for each item
            existing_variation = item.variations.all()
            existing_variation_list.append(list(existing_variation))
            id.append(item.id)

        if product_variation in existing_variation_list:
            index = existing_variation_list.index(product_variation)
            # Get the item id of the correct cart item to increse the quantity of the correct cart item
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()
    return redirect('view_cart')


def remove_from_cart(request, product_id, cart_item_id):
    """ A view to decrese items number from the cart """

    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id)
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
        messages.error(request, f'Error removing item: {e} from your cart!')
    return redirect('view_cart')


def remove_cart_item(request, product_id, cart_item_id):
    """ A view to remove items from the cart """

    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(
        product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    messages.success(request, f'Removed {product.name} from your cart!')
    return redirect('view_cart')

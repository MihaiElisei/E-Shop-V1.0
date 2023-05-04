from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import UserProfile
from checkout.models import Order
from .forms import UserProfileForm, ProductForm

# Create your views here.


def profile(request):
    """Display the user profile"""

    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
    form = UserProfileForm(instance=profile)

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'on_profile_page': True,
    }

    return render(request, template, context)


def my_orders(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    orders = profile.orders.all()
    template = 'profiles/my_orders.html'
    context = {
        'orders': orders,
    }
    return render(request, template, context)


def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)


def add_product(request):
    """Add a product to the store"""

    form = ProductForm
    template = 'profiles/add_product.html'
    context = {
        'form': form
    }
    return render(request, template, context)

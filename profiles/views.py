from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import UserProfile
from checkout.models import Order
from products.models import Product
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
        else:
            messages.error(request, "Update failed. Please review the form!")
    else:
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
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect(reverse('add_product'))
        else:
            messages.error(
                request, "Faild to add product. Please review the form!")
    else:
        form = ProductForm()
    template = 'profiles/add_product.html'
    context = {
        'form': form
    }
    return render(request, template, context)


def edit_product(request, product_id):
    """Edit a product in store"""
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product was updated successfully!")
            return redirect(reverse('product_detail', args=[product_id]))
        else:
            messages.error(
                request, "Faild to update product. Please review the form!")
    else:
        form = ProductForm(instance=product)
        messages.info(request, f"You are editing {product.name}")

    template = 'profiles/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }
    return render(request, template, context)

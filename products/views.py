from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db.models.functions import Lower
from django.db.models import Q
from .models import Product, Category
from cart.models import Cart, CartItem
from cart.views import _cart_id

# Create your views here.


def all_products(request, category_slug=None):
    """ A view to show all products, including sorting and search queries """

    categories = None
    products = None
    query = None
    sort = None
    direction = None

    if category_slug is not None:
        categories = get_object_or_404(
            Category, slug=category_slug
        )
        products = Product.objects.filter(
            category=categories, is_available=True
        )
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')

    # Search and sort products
    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request,
                               ("You didn't enter any search criteria!"))
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(
                description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details"""
    try:
        product = get_object_or_404(Product, pk=product_id)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(
            request), product=product).exists()   # Check if the item is in cart
    except Exception as e:
        raise e

    context = {
        'product': product,
        'in_cart': in_cart,
    }

    return render(request, 'products/product_detail.html', context)

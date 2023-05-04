from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db.models.functions import Lower
from django.db.models import Q
from .models import Product, Category, ReviewRating
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
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

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'product': product,
        'in_cart': in_cart,
        'reviews': reviews,
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def submit_review(request, product_id):
    """A view to handle reviews for products"""
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, "Thank you for your review")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(
                    request, "Thank you! Your review has beem submitted")
                return redirect(url)

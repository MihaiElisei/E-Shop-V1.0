from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<slug:category_slug>/', views.all_products,
         name='products_by_category'),
    path('<product_id>', views.product_detail, name='product_detail'),
    path('submit_review/<int:product_id>',
         views.submit_review, name='submit_review'),
]

from django.urls import path
from . import views


urlpatterns = [
    path('', views.profile, name='profiles'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_history/<order_number>',
         views.order_history,
         name='order_history'),
    path('add/', views.add_product, name='add_product'),

]

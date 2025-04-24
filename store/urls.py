# store/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product-list'),  # List products
    path('cart/', views.view_cart, name='view-cart'),  # View cart
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add-to-cart'),  # Add product to cart
    path('order/', views.place_order, name='place-order'),  # Place an order
    path('session/', views.show_session_key, name='session-key'),

]

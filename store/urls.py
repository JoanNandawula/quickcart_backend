from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('products/<int:id>/', views.product_detail),
    path('products/', views.product_list, name='product_list'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('place-order/', views.place_order),
    path('cart/', views.view_cart),
]

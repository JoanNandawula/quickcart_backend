from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    MyTokenObtainPairView,
    RegisterView,
    home,
    ProductDetailView,
    product_list,
    view_cart,
    add_to_cart,
    place_order,
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    

    # Product endpoints
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    # Cart and order endpoints
    path('cart/', view_cart, name='view-cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add-to-cart'),
    path('order/place/', place_order, name='place-order'),
]
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    MyTokenObtainPairView,
    RegisterView,
    home,
    ProductDetailView,
    product_list,
    view_cart,
    add_to_cart,
    place_order,
    AdminProductViewSet,
    AdminOrderListView,
)
from rest_framework.routers import DefaultRouter

# Set up router for Admin product management
router = DefaultRouter()
router.register(r'admin/products', AdminProductViewSet, basename='admin-products')

urlpatterns = [
    # Authentication & Registration
    path('', home, name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Product endpoints
    path('products/', product_list, name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    # Cart and order endpoints
    path('cart/', view_cart, name='view-cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add-to-cart'),
    path('order/place/', place_order, name='place-order'),

    # Admin order view
    path('api/admin/orders/', AdminOrderListView.as_view(), name='admin-order-list'),

    # Admin Product endpoints
    path('api/', include(router.urls)),  # Include the router URLs under 'api/'
]

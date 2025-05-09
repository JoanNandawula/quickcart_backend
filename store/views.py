from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.generics import RetrieveAPIView
from .models import Product, Cart, CartItem, Order, OrderItem
from .serializers import ProductSerializer, UserSerializer
from rest_framework import viewsets, permissions
from .serializers import AdminProductSerializer
from .serializers import AdminOrderSerializer
from django.views.decorators.csrf import csrf_exempt

class AdminOrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = AdminOrderSerializer
    permission_classes = [permissions.IsAdminUser]
User = get_user_model()

# JWT login with extra user info
class AdminProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = AdminProductSerializer
    permission_classes = [permissions.IsAdminUser]
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'username': self.user.username,
            'email': self.user.email,
            'is_customer': getattr(self.user, 'is_customer', False),
            'is_admin_user': getattr(self.user, 'is_admin_user', True),
        })
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# Register user
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

# Welcome view

@csrf_exempt
def home(request):
    return HttpResponse("Welcome to the Home page!")

# Product list
@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    products = Product.objects.all()
    data = [
        {
            "id": p.id,
            "name": p.name,
            "image_url": p.image.url if p.image else "",
            "price": p.price,
            "category": p.category,
            "stock": p.stock
        } for p in products
    ]
    return Response({"products": data})

# Product detail
class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

# Add product to cart
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return Response({"message": f"Added {product.name} to your cart."}, status=status.HTTP_200_OK)

# View cart
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        items = []
        total = 0
        for item in cart_items:
            subtotal = item.product.price * item.quantity
            items.append({
                "product": item.product.name,
                "quantity": item.quantity,
                "subtotal": subtotal
            })
            total += subtotal
        return Response({"cart_items": items, "total": total})
    except Cart.DoesNotExist:
        return Response({"cart_items": [], "total": 0})

# Place order
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, status='pending', total=0)
        total = 0
        order_items_data = []

        for item in cart_items:
            subtotal = item.product.price * item.quantity
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                subtotal=subtotal
            )
            total += subtotal
            order_items_data.append({
                "product": item.product.name,
                "quantity": item.quantity,
                "subtotal": subtotal
            })

        order.total = total
        order.status = 'completed'
        order.save()
        cart_items.delete()

        return Response({
            "message": "Order placed successfully",
            "order_id": order.id,
            "total": total,
            "items": order_items_data
        })

    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_400_BAD_REQUEST)

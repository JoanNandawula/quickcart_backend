# quickcart_backend/views.py

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET


def show_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return JsonResponse({"session_key": request.session.session_key})

def home(request):
    return HttpResponse("<h1>Welcome to QuickCart Backend</h1><p>Use the /api/ endpoints.</p>")


# List products (simplified, no serializer)



def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)
    data = {
        "id": product.id,
        "name": product.name,
        "image_url": product.image.url,
        "price": product.price,
        "category": product.category,
        "stock": product.stock
    }
    return JsonResponse(data)

def product_list(request):
    products = Product.objects.all()
    product_data = [
        {
            "name": product.name,
            "image_url": product.image.url,
            "price": product.price,
            "category": product.category,
            "stock": product.stock
        }
        for product in products
    ]
    return JsonResponse({"products": product_data})

# View cart items (for user session or logged-in user)
def view_cart(request):
    cart = Cart.objects.get(user=request.user) if request.user.is_authenticated else Cart.objects.get(session_key=request.session.session_key)
    cart_items = CartItem.objects.filter(cart=cart)
    items = [
        {
            "product": item.product.name,
            "quantity": item.quantity,
            "subtotal": item.subtotal
        } for item in cart_items
    ]
    return JsonResponse({"cart_items": items})

# Add product to cart


@csrf_exempt  # Optional: only use this if testing without CSRF token from frontend
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        
        # Check if user is logged in or use session-based cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            cart_key = request.session.session_key
            if not cart_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(session_key=cart_key)
        
        # Add or update the CartItem
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
        cart_item.save()

        return JsonResponse({"message": f"Added {product.name} to your cart."})

    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


# Place order (for checking out)
def place_order(request):
    if request.method == 'POST' and request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        # Create the order
        order = Order.objects.create(user=request.user, status='pending', total=0)

        # Add OrderItems to the order
        total = 0
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                subtotal=cart_item.subtotal
            )
            total += order_item.subtotal

        # Update order total and status
        order.total = total
        order.status = 'completed'  # For simplicity, we're marking it as completed
        order.save()

        # Clear the cart after the order is placed
        cart_items.delete()

        return JsonResponse({"message": f"Order placed successfully. Total: {total}"})
    return JsonResponse({"error": "Failed to place order"}, status=400)

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem


def get_cart(request):
    """Get or create cart for current session"""
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key
    
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def cart_detail(request):
    """Display cart contents"""
    cart = get_cart(request)
    context = {
        'cart': cart,
        'items': cart.items.all(),
        'total': cart.get_total(),
        'total_items': cart.get_total_items(),
    }
    return render(request, 'cart/cart_detail.html', context)

def add_to_cart(request, product_id):
    """Add product to cart with AJAX support"""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = get_cart(request)
    
    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # Get updated cart count
    cart_total = cart.get_total_items()
    
    # Check if AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Added {product.name} to cart! 🌿',
            'cart_total': cart_total,
            'product_name': product.name,
            'product_price': str(product.price),
        })
    
    # Regular POST request
    messages.success(request, f'Added {product.name} to cart!')
    return redirect('cart:cart_detail')

def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.info(request, f'Removed {product_name} from cart')
    return redirect('cart:cart_detail')

def update_cart(request, item_id):
    """Update item quantity"""
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    
    return redirect('cart:cart_detail')

def clear_cart(request):
    """Clear all items from cart"""
    cart = get_cart(request)
    cart.clear()
    messages.info(request, 'Cart cleared')
    return redirect('cart:cart_detail')

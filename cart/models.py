from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    """Shopping cart model"""
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart {self.session_key[:10]}..."
    
    def get_total(self):
        """Calculate total cart price"""
        return sum(item.get_total() for item in self.items.all())
    
    def get_total_items(self):
        """Count total items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()

class CartItem(models.Model):
    """Individual item in cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def get_total(self):
        """Calculate total for this item"""
        return self.product.price * self.quantity
    
    def get_price(self):
        """Get product price"""
        return self.product.price

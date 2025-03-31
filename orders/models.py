from django.db import models
from django.conf import settings
from products.models import Product
import uuid

class Cart(models.Model):
    cart_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.cart_id:
            # Generate a unique ID in production
            self.cart_id = f"cart_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
    
    def add_item(self, product, quantity):
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product_id=product.product_id,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item
    
    def remove_item(self, product_id):
        CartItem.objects.filter(cart=self, product_id=product_id).delete()
    
    def checkout(self):
        # Create an order from the cart
        from orders.services import OrderService
        return OrderService.create_order_from_cart(self)
    
    def __str__(self):
        return f"Cart {self.cart_id} - {'Authenticated' if self.user else 'Guest'}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def product(self):
        try:
            return Product.objects.get(product_id=self.product_id)
        except Product.DoesNotExist:
            return None
    
    @property
    def total_price(self):
        if self.product:
            return self.product.price * self.quantity
        return 0
    
    def __str__(self):
        return f"{self.quantity} of {self.product_id} in cart {self.cart.cart_id}"

class ShippingInfo(models.Model):
    shipping_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.shipping_address}, {self.city}, {self.country}"

class Order(models.Model):
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    
    ORDER_STATUS = (
        ('CREATED', 'Created'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    
    order_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='CREATED')
    shipping_info = models.ForeignKey(ShippingInfo, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate a unique ID in production
            self.order_id = f"order_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
    
    def process_payment(self, payment_info):
        # In production, integrate with Stripe or another payment processor
        payment = Payment.objects.create(
            order=self,
            amount=self.total_amount,
            payment_status='PENDING'
        )
        return payment.process_payment(payment_info)
    
    def calculate_total(self):
        subtotal = sum(item.price * item.quantity for item in self.items.all())
        tax = subtotal * (self.tax_rate / 100)
        return subtotal + tax + self.shipping_cost
    
    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} of {self.product_id} in order {self.order.order_id}"

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    
    payment_id = models.CharField(max_length=50, unique=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            # Generate a unique ID in production
            self.payment_id = f"payment_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
    
    def process_payment(self, payment_info):
        # In production, integrate with Stripe or another payment processor
        # Simulating payment success
        self.payment_status = 'COMPLETED'
        self.transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
        self.save()
        
        # Update order status
        self.order.payment_status = 'PAID'
        self.order.order_status = 'PROCESSING'
        self.order.save()
        return True
    
    def refund_payment(self):
        # In production, integrate with Stripe or another payment processor for refunds
        self.payment_status = 'REFUNDED'
        self.save()
        
        # Update order status
        self.order.payment_status = 'REFUNDED'
        self.order.order_status = 'CANCELLED'
        self.order.save()
        return True
    
    def __str__(self):
        return f"Payment {self.payment_id} for order {self.order.order_id}"

class Promotion(models.Model):
    promotion_id = models.CharField(max_length=50, unique=True)
    discount_code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    expiry_date = models.DateField()
    
    def save(self, *args, **kwargs):
        if not self.promotion_id:
            # Generate a unique ID in production
            self.promotion_id = f"promo_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
    
    def apply_discount(self, order):
        from django.utils import timezone
        if timezone.now().date() <= self.expiry_date:
            discount_amount = order.total_amount * (self.discount_percentage / 100)
            order.total_amount -= discount_amount
            order.save()
            return True
        return False
    
    def __str__(self):
        return f"{self.discount_code} - {self.discount_percentage}% off"

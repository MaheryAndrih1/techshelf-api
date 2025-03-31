from rest_framework import serializers
from .models import Cart, CartItem, ShippingInfo, Order, OrderItem, Payment, Promotion

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'product_name', 'quantity', 'total_price']
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else f"Unknown Product ({obj.product_id})"

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['cart_id', 'user', 'items', 'total', 'created_at', 'updated_at']
        read_only_fields = ['cart_id', 'user', 'created_at', 'updated_at']
    
    def get_total(self, obj):
        return sum(item.total_price for item in obj.items.all())

class ShippingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingInfo
        fields = ['id', 'shipping_address', 'city', 'country', 'postal_code']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    shipping_info = ShippingInfoSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.SerializerMethodField()  
    customer_name = serializers.SerializerMethodField()  
    
    class Meta:
        model = Order
        fields = ['order_id', 'user', 'username', 'customer_name', 'total_amount', 'tax_rate', 'shipping_cost', 
                 'payment_status', 'order_status', 'shipping_info', 'items', 
                 'created_at', 'updated_at']
        read_only_fields = ['order_id', 'user', 'created_at', 'updated_at']
    
    def get_username(self, obj):
        """Return the username of the order's user"""
        return obj.user.username if obj.user else None
    
    def get_customer_name(self, obj):
        """Return a user-friendly name for the customer"""
        if not obj.user:
            return 'Guest User'
        
        # Try to build a full name if available
        first_name = getattr(obj.user, 'first_name', '')
        last_name = getattr(obj.user, 'last_name', '')
        
        if first_name or last_name:
            return f"{first_name} {last_name}".strip()
        
        # Fall back to username if no name available
        return obj.user.username

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('payment_id', 'order', 'amount', 'payment_status', 'transaction_id',
                  'created_at', 'updated_at')
        read_only_fields = ('payment_id', 'created_at', 'updated_at')

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['promotion_id', 'discount_code', 'discount_percentage', 'expiry_date']
        read_only_fields = ['promotion_id']

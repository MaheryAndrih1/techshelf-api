from django.contrib import admin
from .models import Cart, CartItem, ShippingInfo, Order, OrderItem, Payment, Promotion

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'user', 'created_at', 'updated_at')
    search_fields = ('cart_id', 'user__username')
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'

class ShippingInfoAdmin(admin.ModelAdmin):
    list_display = ('shipping_address', 'city', 'country', 'postal_code')
    search_fields = ('shipping_address', 'city', 'country', 'postal_code')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'payment_status', 'order_status', 'created_at')
    list_filter = ('payment_status', 'order_status')
    search_fields = ('order_id', 'user__username')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order', 'amount', 'payment_status', 'created_at')
    list_filter = ('payment_status',)
    search_fields = ('payment_id', 'order__order_id', 'transaction_id')
    date_hierarchy = 'created_at'

class PromotionAdmin(admin.ModelAdmin):
    list_display = ('promotion_id', 'discount_code', 'discount_percentage', 'expiry_date')
    search_fields = ('promotion_id', 'discount_code')

admin.site.register(Cart, CartAdmin)
admin.site.register(ShippingInfo, ShippingInfoAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Promotion, PromotionAdmin)

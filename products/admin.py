from django.contrib import admin
from .models import Product, Like

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'store', 'created_at')
    list_filter = ('category', 'store')
    search_fields = ('name', 'description', 'category')
    readonly_fields = ('product_id',)
    date_hierarchy = 'created_at'

class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'timestamp')
    search_fields = ('user__username', 'product__name')
    date_hierarchy = 'timestamp'

admin.site.register(Product, ProductAdmin)
admin.site.register(Like, LikeAdmin)

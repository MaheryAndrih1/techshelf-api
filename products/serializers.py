from rest_framework import serializers
from .models import Product, Like

class ProductSerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField()
    store_name = serializers.SerializerMethodField()
    store_subdomain = serializers.SerializerMethodField()  # Add this field
    like_count = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'price', 'stock', 'category', 'description', 
                 'image', 'store', 'store_name', 'store_subdomain',  # Include store_subdomain
                 'created_at', 'updated_at',
                 'like_count', 'is_liked']
        read_only_fields = ['product_id', 'store', 'created_at', 'updated_at', 
                           'store_name', 'store_subdomain', 'like_count', 'is_liked']
    
    def get_store_name(self, obj):
        return obj.store.store_name if obj.store else None
    
    # Add this method to get the store's subdomain
    def get_store_subdomain(self, obj):
        return obj.store.subdomain_name if obj.store else None

    def get_like_count(self, obj):
        return obj.likes.count()
        
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'category', 'description', 'image']
    
    def create(self, validated_data):
        # Get the store from the context
        store = self.context['request'].user.store
        
        # Remove store from validated_data if it exists to prevent duplicate
        if 'store' in validated_data:
            validated_data.pop('store')
            
        # Create the product with the store
        product = Product.objects.create(store=store, **validated_data)
        return product

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['like_id', 'user', 'product', 'timestamp']
        read_only_fields = ['like_id', 'user', 'timestamp']

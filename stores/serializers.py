from rest_framework import serializers
from .models import Store, StoreTheme, Rating

class StoreThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreTheme
        fields = ['theme_id', 'primary_color', 'secondary_color', 'font', 'logo_url', 'banner_url']

class StoreSerializer(serializers.ModelSerializer):
    theme = StoreThemeSerializer(read_only=True)
    user = serializers.StringRelatedField()
    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Store
        fields = ['store_id', 'store_name', 'subdomain_name', 'user', 'theme', 'created_at', 'average_rating', 'rating_count']
        read_only_fields = ['store_id', 'user', 'created_at', 'average_rating', 'rating_count']
    
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings.exists():
            return None
        return sum(rating.score for rating in ratings) / ratings.count()
    
    def get_rating_count(self, obj):
        return obj.ratings.count()

class StoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['store_name', 'subdomain_name']
        
    def validate_subdomain_name(self, value):
        if value and Store.objects.filter(subdomain_name=value).exists():
            raise serializers.ValidationError("This subdomain is already taken.")
        return value

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Rating
        fields = ['rating_id', 'user', 'score', 'comment', 'timestamp']
        read_only_fields = ['rating_id', 'user', 'timestamp']

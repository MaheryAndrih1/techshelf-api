from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import BillingInfo

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class BillingInfoSerializer(serializers.ModelSerializer):
    card_number = serializers.SerializerMethodField()
    
    class Meta:
        model = BillingInfo
        fields = ['card_number', 'expiry_date', 'billing_address']
    
    def get_card_number(self, obj):
        if obj.card_number:
            # Mask all but the last 4 digits
            return '**** **** **** ' + obj.card_number[-4:]
        return None
    
    def create(self, validated_data):
        user = self.context['request'].user
        billing_info, _ = BillingInfo.objects.update_or_create(
            user=user,
            defaults=validated_data
        )
        return billing_info

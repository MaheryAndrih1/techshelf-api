from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_ROLES = (
        ('BUYER', 'Buyer'),
        ('SELLER', 'Seller'),
        ('ADMIN', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='BUYER')
    
    def upgrade_to_seller(self):
        self.role = 'SELLER'
        self.save()
    
    def __str__(self):
        return self.username

class BillingInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='billing_info')
    card_number = models.CharField(max_length=255)  # Encrypted in production
    expiry_date = models.CharField(max_length=7)  # Format: MM/YYYY
    cvv = models.CharField(max_length=4)  # Encrypted in production
    billing_address = models.TextField()
    
    def __str__(self):
        return f"Billing info for {self.user.username}"

class Authentication:
    @staticmethod
    def authenticate(email, password):
        from django.contrib.auth import authenticate
        user = authenticate(username=email, password=password)
        return user
    
    @staticmethod
    def is_authenticated(request):
        return request.user.is_authenticated

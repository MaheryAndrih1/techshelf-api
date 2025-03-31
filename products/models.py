from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.product_id:
            # Generate a unique ID in production
            self.product_id = f"prod_{slugify(self.name)}"
        super().save(*args, **kwargs)
    
    @property
    def likes(self):
        return self.like_set.count()
    
    def update_price(self, new_price):
        self.price = new_price
        self.save()
    
    def add_like(self):
        # This is handled by the Like model's creation
        pass
    
    def decrement_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
    
    def __str__(self):
        return self.name

class Like(models.Model):
    like_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
    
    def save(self, *args, **kwargs):
        if not self.like_id:
            # Generate a unique ID in production
            self.like_id = f"like_{self.user.id}_{self.product.product_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} liked {self.product.name}"

class ProductLike(models.Model):
    like_id = models.CharField(max_length=100, primary_key=True, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='product_likes')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
        
    def save(self, *args, **kwargs):
        if not self.like_id:
            self.like_id = f"like_{self.product.product_id}_{self.user.id}"
        super().save(*args, **kwargs)

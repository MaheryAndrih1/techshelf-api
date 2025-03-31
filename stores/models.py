from django.db import models
from django.conf import settings
from django.utils.text import slugify

class StoreTheme(models.Model):
    theme_id = models.CharField(max_length=50, unique=True)
    primary_color = models.CharField(max_length=20, default='#3498db')
    secondary_color = models.CharField(max_length=20, default='#2ecc71')
    font = models.CharField(max_length=50, default='Roboto')
    logo_url = models.ImageField(upload_to='store_logos/', null=True, blank=True)
    banner_url = models.ImageField(upload_to='store_banners/', null=True, blank=True)
    
    def __str__(self):
        return self.theme_id

class Store(models.Model):
    store_id = models.CharField(max_length=50, unique=True, blank=True)
    store_name = models.CharField(max_length=255)
    subdomain_name = models.SlugField(unique=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='store')
    theme = models.ForeignKey(StoreTheme, on_delete=models.SET_NULL, null=True, blank=True, related_name='stores')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Generate subdomain_name from store_name if not provided
        if not self.subdomain_name and self.store_name:
            base_slug = slugify(self.store_name)
            slug = base_slug
            
            # Make sure slugified name is unique
            counter = 1
            while Store.objects.filter(subdomain_name=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.subdomain_name = slug
        
        # Generate store_id if not provided
        if not self.store_id and self.subdomain_name:
            self.store_id = f"store_{self.subdomain_name}"
            
        super().save(*args, **kwargs)
    
    def add_product(self, product):
        product.store = self
        product.save()
        return product
    
    def remove_product(self, product_id):
        from products.models import Product
        Product.objects.filter(product_id=product_id, store=self).delete()
    
    def update_product(self, product):
        product.save()
        return product
    
    def set_subdomain(self, subdomain):
        self.subdomain_name = slugify(subdomain)
        self.save()
    
    def update_theme(self, theme):
        self.theme = theme
        self.save()
    
    def __str__(self):
        return self.store_name

class Rating(models.Model):
    rating_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 rating
    comment = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'store')
    
    def __str__(self):
        return f"{self.user.username}'s {self.score} star rating for {self.store.store_name}"

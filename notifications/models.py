from django.db import models
from django.conf import settings
import uuid

class Notification(models.Model):
    notification_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.notification_id:
            # Generate a unique ID in production
            self.notification_id = f"notif_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
    
    @classmethod
    def send_notification(cls, user, message):
        """Utility method to easily send notifications"""
        notification = cls.objects.create(
            user=user,
            message=message
        )
        # You could trigger email/push notifications here
        return notification
    
    def send_email(self):
        # In production, integrate with email service
        from django.core.mail import send_mail
        send_mail(
            'Notification from TechShelf',
            self.message,
            'noreply@techshelf.com',
            [self.user.email],
            fail_silently=False,
        )
    
    def send_sms(self):
        # In production, integrate with SMS service like Twilio
        pass
    
    def __str__(self):
        return f"Notification to {self.user.username}: {self.message[:30]}..."

class SalesReport(models.Model):
    report_id = models.CharField(max_length=50, unique=True)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='sales_reports')
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    report_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def save(self, *args, **kwargs):
        if not self.report_id:
            # Generate a unique ID in production
            self.report_id = f"report_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_report(store, start_date, end_date):
        from django.db.models import Sum, F, ExpressionWrapper, DecimalField
        from django.db.models.functions import Coalesce
        from orders.models import OrderItem
        
        # Find all orders for products from this store in the date range
        order_items = OrderItem.objects.filter(
            product_id__in=store.products.values_list('product_id', flat=True),
            order__created_at__date__range=(start_date, end_date),
            order__payment_status='PAID'
        )
        
        # Calculate total sales
        total_sales = order_items.annotate(
            item_total=ExpressionWrapper(
                F('price') * F('quantity'),
                output_field=DecimalField()
            )
        ).aggregate(
            total=Coalesce(Sum('item_total'), 0.0)
        )['total']
        
        # Get top products
        from products.models import Product
        top_products = Product.objects.filter(
            product_id__in=order_items.values_list('product_id', flat=True),
            store=store
        ).annotate(
            sold_quantity=Coalesce(Sum('orderitem__quantity'), 0),
            sales_amount=Coalesce(
                Sum(ExpressionWrapper(
                    F('orderitem__price') * F('orderitem__quantity'),
                    output_field=DecimalField()
                )), 0.0
            )
        ).order_by('-sales_amount')
        
        # Create report
        report = SalesReport.objects.create(
            store=store,
            total_sales=total_sales,
            start_date=start_date,
            end_date=end_date
        )
        
        return report
    
    def __str__(self):
        return f"Sales Report for {self.store.store_name} ({self.start_date} to {self.end_date})"

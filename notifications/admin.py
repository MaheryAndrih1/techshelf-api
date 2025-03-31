from django.contrib import admin
from .models import Notification, SalesReport

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'message')
    date_hierarchy = 'created_at'

class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'store', 'total_sales', 'start_date', 'end_date', 'report_date')
    search_fields = ('report_id', 'store__store_name')
    date_hierarchy = 'report_date'

admin.site.register(Notification, NotificationAdmin)
admin.site.register(SalesReport, SalesReportAdmin)

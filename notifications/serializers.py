from rest_framework import serializers
from .models import Notification, SalesReport

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['notification_id', 'user', 'message', 'is_read', 'created_at']
        read_only_fields = ['notification_id', 'user', 'created_at']

class SalesReportSerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField()
    store_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesReport
        fields = ['report_id', 'store', 'store_name', 'total_sales', 'report_date', 'start_date', 'end_date']
        read_only_fields = ['report_id', 'store', 'report_date']
    
    def get_store_name(self, obj):
        return obj.store.store_name if obj.store else None

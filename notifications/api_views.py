from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Notification, SalesReport
from .serializers import NotificationSerializer, SalesReportSerializer
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
import logging
import traceback

logger = logging.getLogger(__name__)

class NotificationListView(generics.ListAPIView):
    """List all notifications for the authenticated user"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user).order_by('-created_at')
        
        store_id = self.request.query_params.get('store_id')
        if store_id and hasattr(self.request.user, 'store') and self.request.user.store.store_id == store_id:
            store_notifications = queryset.filter(
                Q(message__icontains=store_id) | 
                Q(message__icontains=self.request.user.store.store_name)
            )
            return store_notifications
        
        return queryset

class MarkNotificationReadView(APIView):
    """Mark a notification as read - supports both POST and PUT/PATCH methods"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, notification_id):
        return get_object_or_404(Notification, 
                                notification_id=notification_id,
                                user=self.request.user)
    
    def post(self, request, notification_id):
        notification = self.get_object(notification_id)
        notification.is_read = True
        notification.save()
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
    
    def put(self, request, notification_id):
        notification = self.get_object(notification_id)
        notification.is_read = True
        notification.save()
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
    
    def patch(self, request, notification_id):
        notification = self.get_object(notification_id)
        notification.is_read = True
        notification.save()
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

class SalesReportListView(generics.ListAPIView):
    """List all sales reports for the authenticated seller's store"""
    serializer_class = SalesReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role != 'SELLER' or not hasattr(self.request.user, 'store'):
            return SalesReport.objects.none()
        
        return SalesReport.objects.filter(store=self.request.user.store).order_by('-report_date')

class GenerateReportView(APIView):
    """Generate a new sales report"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            logger.debug(f"Report generation request received: {request.data}")
            
            if request.user.role != 'SELLER':
                return Response({'error': 'Only sellers can generate sales reports'}, status=status.HTTP_403_FORBIDDEN)
            
            if not hasattr(request.user, 'store'):
                return Response({'error': 'You need to create a store first'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                start_date = request.data.get('start_date')
                end_date = request.data.get('end_date')
                
                if not start_date:
                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
                if not end_date:
                    end_date = datetime.now().strftime('%Y-%m-%d')
                
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError as e:
                logger.error(f"Date format error: {e}")
                return Response({'error': f'Invalid date format: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                report = SalesReport.objects.create(
                    report_id=f"report_{request.user.store.store_id}_{int(datetime.now().timestamp())}",
                    store=request.user.store,
                    total_sales=0.0,
                    start_date=start_date_obj,
                    end_date=end_date_obj
                )
                
                serializer = SalesReportSerializer(report)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Report creation error: {e}")
                logger.error(traceback.format_exc())
                return Response({'error': f'Error creating report: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Unexpected error in report generation: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SalesReportDetailView(generics.RetrieveAPIView):
    """Get details of a specific sales report"""
    serializer_class = SalesReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'report_id'
    
    def get_queryset(self):
        if self.request.user.role != 'SELLER' or not hasattr(self.request.user, 'store'):
            return SalesReport.objects.none()
        
        return SalesReport.objects.filter(store=self.request.user.store)

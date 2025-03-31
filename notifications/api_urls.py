from django.urls import path
from .api_views import (
    NotificationListView, MarkNotificationReadView,
    SalesReportListView, GenerateReportView, SalesReportDetailView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='api_notification_list'),
    path('<str:notification_id>/read/', MarkNotificationReadView.as_view(), name='api_notification_mark_read'),
    path('reports/', SalesReportListView.as_view(), name='api_sales_report_list'),
    path('reports/generate/', GenerateReportView.as_view(), name='api_generate_report'),
    path('reports/<str:report_id>/', SalesReportDetailView.as_view(), name='api_sales_report_detail'),
]

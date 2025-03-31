from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list_view, name='list'),
    path('<str:notification_id>/mark-read/', views.mark_notification_read_view, name='mark_read'),
    path('reports/', views.sales_reports_view, name='reports'),
    path('reports/generate/', views.generate_report_view, name='generate_report'),
    path('reports/<str:report_id>/', views.report_detail_view, name='report_detail'),
]

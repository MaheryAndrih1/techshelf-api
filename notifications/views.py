from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification, SalesReport
from django.utils import timezone
from datetime import datetime

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_notification_read_view(request, notification_id):
    notification = get_object_or_404(Notification, notification_id=notification_id, user=request.user)
    
    if request.method == 'POST':
        notification.is_read = True
        notification.save()
        messages.success(request, 'Notification marked as read.')
    
    return redirect('notifications:list')

@login_required
def sales_reports_view(request):
    # Check if user is a seller
    if request.user.role != 'SELLER':
        messages.error(request, 'Only sellers can access sales reports.')
        return redirect('users:profile')
    
    # Get store and reports
    if hasattr(request.user, 'store'):
        reports = SalesReport.objects.filter(store=request.user.store).order_by('-report_date')
    else:
        reports = []
    
    return render(request, 'notifications/reports.html', {'reports': reports})

@login_required
def generate_report_view(request):
    # Check if user is a seller
    if request.user.role != 'SELLER':
        messages.error(request, 'Only sellers can generate sales reports.')
        return redirect('users:profile')
    
    # Check if user has a store
    if not hasattr(request.user, 'store'):
        messages.error(request, 'You need to create a store first.')
        return redirect('stores:create')
    
    if request.method == 'POST':
        # Validate dates
        try:
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            # Convert strings to date objects for validation
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Check date range
            if start_date_obj > end_date_obj:
                messages.error(request, 'Start date cannot be after end date.')
                return redirect('notifications:reports')
                
            # Check if end date is in the future
            if end_date_obj > timezone.now().date():
                messages.error(request, 'End date cannot be in the future.')
                return redirect('notifications:reports')
                
            # Generate report
            report = SalesReport.generate_report(
                store=request.user.store,
                start_date=start_date,
                end_date=end_date
            )
            
            messages.success(request, 'Sales report generated successfully.')
            return redirect('notifications:report_detail', report_id=report.report_id)
        except ValueError as e:
            messages.error(request, f'Invalid date format: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error generating report: {str(e)}')
    
    return redirect('notifications:reports')

@login_required
def report_detail_view(request, report_id):
    # Check if user is a seller
    if request.user.role != 'SELLER':
        messages.error(request, 'Only sellers can access sales reports.')
        return redirect('users:profile')
    
    # Get report
    report = get_object_or_404(SalesReport, report_id=report_id)
    
    # Check if user owns this store
    if report.store.user != request.user:
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('notifications:reports')
    
    return render(request, 'notifications/report_detail.html', {'report': report})

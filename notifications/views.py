from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Notification


@login_required
def notification_list_view(request):
    """Lists all notifications for the current authenticated user."""
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
    })


@login_required
@require_POST
def mark_notification_read_view(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    
    if notif.order:
        return redirect('accounts:order_detail', order_number=notif.order.order_number)
    return redirect('notifications:notification_list')


@login_required
@require_POST
def mark_all_read_view(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications:notification_list')

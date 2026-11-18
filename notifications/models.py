from django.db import models
from django.conf import settings
from orders.models import Order


class Notification(models.Model):
    """
    In-app and customer account notifications.
    Keeps customer updated on order status and payment verification in real time.
    """
    TYPE_CHOICES = [
        ('ORDER_PLACED', 'Order Placed'),
        ('PAYMENT_VERIFIED', 'Payment Verified & Approved'),
        ('PAYMENT_REJECTED', 'Payment Rejected'),
        ('PROCESSING', 'Order in Processing'),
        ('SUPPLIER_ORDER_PLACED', 'Procurement in Progress'),
        ('SHIPPED', 'Order Dispatched / Shipped'),
        ('DELIVERED', 'Order Delivered'),
        ('CANCELLED', 'Order Cancelled'),
        ('REFUND', 'Refund Update'),
        ('SYSTEM', 'System Announcement'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=150, verbose_name="Notification Title")
    message = models.TextField(verbose_name="Message Content")
    notification_type = models.CharField(max_length=40, choices=TYPE_CHOICES, default='SYSTEM')
    is_read = models.BooleanField(default=False, verbose_name="Mark as Read")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title} for {self.user.username}"

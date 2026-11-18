from django.db import models
from django.conf import settings
from decimal import Decimal
from orders.models import Order, OrderStatusHistory


class SiteConfiguration(models.Model):
    """
    Storefront and Manual UPI Payment Configuration.
    Allows administrators to configure live UPI details, QR code, and business contact.
    """
    site_name = models.CharField(max_length=100, default="POCKET", verbose_name="Website Name")
    tagline = models.CharField(max_length=200, default="Fashion that fits your pocket.", verbose_name="Official Tagline")
    
    # UPI Configuration (Configurable by Admin)
    upi_id = models.CharField(
        max_length=100,
        default="pocketstore@upi",
        verbose_name="Official Business UPI ID",
        help_text="Verify that your bank/payment provider permits commercial transactions for this UPI ID."
    )
    account_display_name = models.CharField(
        max_length=150,
        default="POCKET FASHION STORE",
        verbose_name="Account Display Name",
        help_text="Name displayed on UPI apps when customer scans QR code"
    )
    qr_code_image = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        verbose_name="UPI QR Code Image",
        help_text="Upload your official business UPI QR code image"
    )
    payment_instructions = models.TextField(
        default=(
            "1. Scan the QR code using Google Pay, PhonePe, Paytm, BHIM, or any UPI app.\n"
            "2. Pay the exact order amount.\n"
            "3. Note down the 12-digit UTR / Bank Reference Number from your payment app.\n"
            "4. Enter the UTR number below and submit your payment.\n"
            "5. Our team verifies the transaction with our bank account before confirming and processing your order."
        ),
        verbose_name="Customer Payment Instructions"
    )

    # Shipping Rules
    free_shipping_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('499.00'),
        verbose_name="Free Shipping Minimum Order (₹)"
    )
    standard_shipping_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('49.00'),
        verbose_name="Standard Shipping Charge (₹)"
    )

    # Business Contact & Support
    support_phone = models.CharField(max_length=30, default="+91 98765 43210", verbose_name="Support Phone")
    support_email = models.EmailField(default="support@pocketfashion.in", verbose_name="Support Email")
    support_hours = models.CharField(max_length=100, default="Mon - Sat: 10:00 AM - 7:00 PM", verbose_name="Support Hours")
    address = models.TextField(default="POCKET Fashion, India", verbose_name="Business Address")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site & Payment Configuration"
        verbose_name_plural = "Site & Payment Configuration"

    @classmethod
    def get_solo(cls):
        """Returns the single configuration instance or creates default."""
        config, created = cls.objects.get_or_create(id=1)
        return config

    def __str__(self):
        return f"{self.site_name} Configuration (UPI: {self.upi_id})"


class Payment(models.Model):
    """
    Customer payment record for orders.
    Supports Manual UPI verification workflow and extensible for future payment gateways.
    """
    PAYMENT_METHOD_CHOICES = [
        ('MANUAL_UPI', 'Manual UPI Transfer'),
        ('RAZORPAY', 'Razorpay Gateway (Future Ready)'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified & Confirmed'),
        ('REJECTED', 'Payment Rejected'),
        ('REFUNDED', 'Refunded'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='MANUAL_UPI')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount Paid (₹)")
    utr_number = models.CharField(max_length=64, db_index=True, verbose_name="12-digit UTR / Reference Number")
    payer_upi_id = models.CharField(max_length=100, blank=True, verbose_name="Customer UPI ID / Number")
    payer_name = models.CharField(max_length=120, blank=True, verbose_name="Payer Account Name")
    payment_screenshot = models.ImageField(upload_to='payments/', blank=True, null=True, verbose_name="Payment Screenshot")
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    admin_notes = models.TextField(blank=True, verbose_name="Admin Verification Notes")
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        verbose_name="Verified By Admin"
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment ₹{self.amount} for {self.order.order_number} ({self.get_status_display()}) - UTR: {self.utr_number}"

    def approve(self, admin_user, notes=""):
        """
        Manually approve payment after checking actual bank/UPI receipt.
        Updates order status to PAYMENT_VERIFIED and logs to status history.
        """
        from django.utils import timezone
        self.status = 'VERIFIED'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        if notes:
            self.admin_notes = notes
        self.save()

        # Update linked order
        order = self.order
        order.payment_status = 'VERIFIED'
        order.status = 'PAYMENT_VERIFIED'
        order.save()

        # Record status history
        OrderStatusHistory.objects.create(
            order=order,
            status='PAYMENT_VERIFIED',
            changed_by=admin_user,
            comment=f"Payment verified via UTR {self.utr_number}. {notes}".strip()
        )

    def reject(self, admin_user, notes=""):
        """
        Reject payment when UTR does not match bank record.
        """
        from django.utils import timezone
        self.status = 'REJECTED'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        if notes:
            self.admin_notes = notes
        self.save()

        # Update linked order
        order = self.order
        order.payment_status = 'FAILED_REJECTED'
        order.save()

        # Record status history
        OrderStatusHistory.objects.create(
            order=order,
            status=order.status,
            changed_by=admin_user,
            comment=f"Payment rejected: UTR {self.utr_number} not verified. Reason: {notes}".strip()
        )

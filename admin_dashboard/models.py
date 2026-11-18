from django.db import models


class Supplier(models.Model):
    """
    Internal supplier record for reselling/procurement operations.
    CRITICAL: This model is internal-only. Never expose to customer-facing pages or APIs.
    """
    PLATFORM_CHOICES = [
        ('MEESHO', 'Meesho Seller'),
        ('FLIPKART', 'Flipkart Seller'),
        ('MANUFACTURER', 'Direct Manufacturer / Wholesaler'),
        ('LOCAL_DISTRIBUTOR', 'Local Distributor'),
        ('OTHER', 'Other Platform / Vendor'),
    ]

    name = models.CharField(max_length=150, verbose_name="Supplier / Shop Name")
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES, default='MEESHO')
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Contact Person")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Contact Phone")
    email = models.EmailField(blank=True, verbose_name="Contact Email")
    website_or_store_url = models.URLField(max_length=500, blank=True, verbose_name="Store / Product URL")
    internal_notes = models.TextField(blank=True, verbose_name="Internal Operational Notes")
    is_active = models.BooleanField(default=True, verbose_name="Active Supplier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"


class BusinessExpense(models.Model):
    """
    Tracks business expenses for accurate financial accounting and net profit reporting.
    """
    EXPENSE_TYPE_CHOICES = [
        ('SHIPPING', 'Outbound Shipping & Courier Charges'),
        ('PACKAGING', 'Packaging Material & Boxes'),
        ('PAYMENT_FEE', 'Payment Gateway / Transfer Charges'),
        ('RETURN_FEE', 'Return / Reverse Logistics Fee'),
        ('MARKETING', 'Promotion / Marketing Expense'),
        ('OTHER', 'Other Operational Expense'),
    ]

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_expenses',
        verbose_name="Linked Order (Optional)"
    )
    expense_type = models.CharField(max_length=30, choices=EXPENSE_TYPE_CHOICES, default='PACKAGING')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Expense Amount (₹)")
    description = models.CharField(max_length=255, verbose_name="Description / Reason")
    expense_date = models.DateField(auto_now_add=True, verbose_name="Expense Date")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Business Expense"
        verbose_name_plural = "Business Expenses"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_expense_type_display()} - ₹{self.amount} ({self.description})"

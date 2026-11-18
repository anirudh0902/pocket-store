import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant
from admin_dashboard.models import Supplier


class Wishlist(models.Model):
    """
    Customer's saved wishlist.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"


class WishlistItem(models.Model):
    """
    Items saved in wishlist.
    """
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wishlist', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s wishlist"


class Cart(models.Model):
    """
    Shopping cart for authenticated customers or guest sessions.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    @property
    def total_items_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def shipping_charge(self):
        if self.subtotal == 0:
            return Decimal('0.00')
        free_threshold = Decimal(str(settings.POCKET_BRAND.get('FREE_SHIPPING_THRESHOLD', 499.00)))
        default_shipping = Decimal(str(settings.POCKET_BRAND.get('DEFAULT_SHIPPING_FEE', 49.00)))
        if self.subtotal >= free_threshold:
            return Decimal('0.00')
        return default_shipping

    @property
    def grand_total(self):
        return self.subtotal + self.shipping_charge

    def __str__(self):
        owner = self.user.username if self.user else f"Guest ({self.session_key[:8]})"
        return f"Cart ({owner}) - {self.total_items_count} items"


class CartItem(models.Model):
    """
    Individual item in a shopping cart.
    Always validated server-side.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ('cart', 'product', 'variant')

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.final_price
        return self.product.selling_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        var_text = f" ({self.variant})" if self.variant else ""
        return f"{self.quantity}x {self.product.name}{var_text}"


class Order(models.Model):
    """
    Complete order record with financial snapshots, delivery address snapshot,
    and internal supplier/expense accounting.
    """
    STATUS_CHOICES = [
        ('PENDING_PAYMENT', 'Pending Payment'),
        ('PAYMENT_VERIFICATION', 'Payment Verification'),
        ('PAYMENT_VERIFIED', 'Payment Verified'),
        ('PROCESSING', 'Processing'),
        ('SUPPLIER_ORDER_PLACED', 'Supplier Order Placed'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUND_PENDING', 'Refund Pending'),
        ('REFUNDED', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('UNPAID', 'Unpaid'),
        ('SUBMITTED', 'Submitted for Verification'),
        ('VERIFIED', 'Verified & Confirmed'),
        ('FAILED_REJECTED', 'Payment Rejected'),
        ('REFUNDED', 'Refunded'),
    ]

    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    
    # Immutable snapshot of delivery address at checkout
    shipping_address_snapshot = models.JSONField(verbose_name="Shipping Address Snapshot")

    # Customer Billing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Order Subtotal (₹)")
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Shipping Fee Charged (₹)")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Payable Amount (₹)")

    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='PENDING_PAYMENT', db_index=True)
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='UNPAID', db_index=True)

    # STRICTLY INTERNAL FINANCIAL SNAPSHOT & EXPENSES
    total_supplier_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Total Supplier Cost (₹)")
    actual_shipping_expense = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Actual Shipping Expense (₹)")
    packaging_expense = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Packaging Material Cost (₹)")
    payment_gateway_charges = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Payment Processing Charges (₹)")
    other_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Other Expenses (₹)")
    estimated_profit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Estimated Net Profit (₹)")

    # STRICTLY INTERNAL SUPPLIER DETAILS
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='supplier_orders', verbose_name="Fulfillment Supplier (Internal)")
    supplier_order_reference = models.CharField(max_length=150, blank=True, verbose_name="Supplier Order ID / Reference")
    supplier_order_date = models.DateTimeField(null=True, blank=True, verbose_name="Supplier Order Placement Date")
    internal_notes = models.TextField(blank=True, verbose_name="Admin Internal Notes (Private)")

    customer_notes = models.TextField(blank=True, verbose_name="Customer Delivery Instructions")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    @classmethod
    def generate_order_number(cls):
        """Generates clean readable unique order number: PKT-YYYYMMDD-XXXX."""
        import datetime, random
        date_str = datetime.date.today().strftime('%Y%m%d')
        random_suffix = ''.join(random.choices('0123456789ABCDEF', k=5))
        number = f"PKT-{date_str}-{random_suffix}"
        while cls.objects.filter(order_number=number).exists():
            random_suffix = ''.join(random.choices('0123456789ABCDEF', k=5))
            number = f"PKT-{date_str}-{random_suffix}"
        return number

    def calculate_profit(self):
        """
        Formula as defined in specification:
        Estimated Profit = Selling Price (Total Amount) - Supplier Cost - Actual Shipping Expense - Packaging - Payment Charges - Other Expenses
        """
        # If cancelled or refunded, profit becomes 0 or negative of incurred expenses
        if self.status in ['CANCELLED', 'REFUNDED']:
            self.estimated_profit = Decimal('0.00') - self.other_expenses - self.packaging_expense
        else:
            total_rev = self.total_amount
            total_exp = (
                self.total_supplier_cost +
                self.actual_shipping_expense +
                self.packaging_expense +
                self.payment_gateway_charges +
                self.other_expenses
            )
            self.estimated_profit = total_rev - total_exp
        return self.estimated_profit

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        self.calculate_profit()
        super().save(*args, **kwargs)

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def latest_payment(self):
        return self.payments.order_by('-created_at').first()

    def __str__(self):
        return f"{self.order_number} ({self.get_status_display()}) - ₹{self.total_amount}"


class OrderItem(models.Model):
    """
    Snapshot of items in order.
    Preserves exact customer selling price and internal supplier cost at time of order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255, verbose_name="Product Name (Snapshot)")
    variant_details = models.CharField(max_length=150, blank=True, verbose_name="Variant (Size/Color)")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Customer Unit Price (₹)")
    supplier_unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Supplier Unit Cost (₹)")
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Customer Amount (₹)")

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    @property
    def item_supplier_cost_total(self):
        return self.supplier_unit_cost * self.quantity

    @property
    def item_gross_margin(self):
        return self.total_price - self.item_supplier_cost_total

    def __str__(self):
        return f"{self.quantity}x {self.product_name} in {self.order.order_number}"


class OrderStatusHistory(models.Model):
    """
    Audit log of all order status changes with timestamp and responsible admin.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=40, choices=Order.STATUS_CHOICES)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(blank=True, verbose_name="Status Change Comment / Reason")
    customer_visible = models.BooleanField(default=True, verbose_name="Visible to Customer")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order Status History"
        verbose_name_plural = "Order Status Histories"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.order_number} -> {self.status} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ShippingDetails(models.Model):
    """
    Courier tracking and dispatch details.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_details')
    courier_partner = models.CharField(max_length=100, verbose_name="Courier / Logistics Partner")
    tracking_number = models.CharField(max_length=120, verbose_name="AWB / Tracking Number")
    tracking_url = models.URLField(max_length=500, blank=True, verbose_name="Online Tracking URL")
    dispatched_date = models.DateTimeField(null=True, blank=True, verbose_name="Dispatched Date & Time")
    estimated_delivery_date = models.DateField(null=True, blank=True, verbose_name="Estimated Delivery Date")
    actual_delivery_date = models.DateTimeField(null=True, blank=True, verbose_name="Actual Delivery Date")
    notes = models.TextField(blank=True, verbose_name="Logistics Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shipping Details"
        verbose_name_plural = "Shipping Details"

    def __str__(self):
        return f"{self.courier_partner} ({self.tracking_number}) for {self.order.order_number}"

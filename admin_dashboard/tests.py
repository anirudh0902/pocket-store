from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from orders.models import Order
from admin_dashboard.models import Supplier


class AdminDashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='boss', email='boss@pocket.in', password='Password123!',
            is_staff=True, is_pocket_admin=True
        )
        self.customer = User.objects.create_user(
            username='shopper', email='shopper@pocket.in', password='Password123!'
        )
        self.supplier = Supplier.objects.create(
            name="Direct Manufacturer Hub",
            platform="MANUFACTURER",
            contact_person="Sharma Ji",
            phone="9876543210"
        )
        # Order setup matching prompt example:
        # Selling Price = ₹599, Supplier Cost = ₹350, Shipping = ₹40, Other Expenses = ₹20 -> Estimated Profit = ₹189
        self.order = Order.objects.create(
            user=self.customer,
            shipping_address_snapshot={'full_name': 'Shopper', 'city': 'Pune', 'pincode': '411001'},
            subtotal=Decimal('599.00'),
            shipping_fee=Decimal('0.00'),
            total_amount=Decimal('599.00'),
            total_supplier_cost=Decimal('350.00'),
            actual_shipping_expense=Decimal('40.00'),
            other_expenses=Decimal('20.00'),
            status='PENDING_PAYMENT',
            payment_status='UNPAID'
        )

    def test_profit_calculation_formula(self):
        """
        Verify exact business formula:
        Estimated Profit = Total Amount - Supplier Cost - Shipping - Packaging - Payment Charges - Other Expenses
        599 - 350 - 40 - 0 - 0 - 20 = 189
        """
        profit = self.order.calculate_profit()
        self.assertEqual(profit, Decimal('189.00'))
        self.assertEqual(self.order.estimated_profit, Decimal('189.00'))

    def test_supplier_fulfillment_blocked_before_payment_verification(self):
        """Supplier order placement MUST be blocked if payment is not verified!"""
        self.client.login(username='boss', password='Password123!')
        
        # Order is currently UNPAID
        response = self.client.post(reverse('admin_dashboard:order_supplier_fulfillment', kwargs={'order_number': self.order.order_number}), {
            'supplier_id': self.supplier.id,
            'supplier_order_reference': 'SUP-123'
        })
        self.assertEqual(response.status_code, 302)
        
        self.order.refresh_from_db()
        # Status should NOT have changed to SUPPLIER_ORDER_PLACED
        self.assertNotEqual(self.order.status, 'SUPPLIER_ORDER_PLACED')

    def test_supplier_fulfillment_allowed_after_payment_verification(self):
        """Supplier ordering succeeds once payment is verified."""
        self.client.login(username='boss', password='Password123!')
        
        self.order.payment_status = 'VERIFIED'
        self.order.status = 'PAYMENT_VERIFIED'
        self.order.save()

        response = self.client.post(reverse('admin_dashboard:order_supplier_fulfillment', kwargs={'order_number': self.order.order_number}), {
            'supplier_id': self.supplier.id,
            'supplier_order_reference': 'SUP-123'
        })
        self.assertEqual(response.status_code, 302)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'SUPPLIER_ORDER_PLACED')
        self.assertEqual(self.order.supplier_order_reference, 'SUP-123')

    def test_customer_cannot_access_admin_portal(self):
        """Non-admin customer must be blocked from accessing admin dashboard!"""
        self.client.login(username='shopper', password='Password123!')
        response = self.client.get(reverse('admin_dashboard:dashboard'))
        # user_passes_test redirects unauthorized users to login
        self.assertEqual(response.status_code, 302)

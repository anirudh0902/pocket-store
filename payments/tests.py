from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from orders.models import Order
from payments.models import Payment, SiteConfiguration


class PaymentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='buyer2', email='buyer2@pocket.in', password='Password123!'
        )
        self.admin = User.objects.create_user(
            username='admin_test', email='adm@pocket.in', password='Password123!',
            is_staff=True, is_pocket_admin=True
        )
        self.order = Order.objects.create(
            user=self.customer,
            shipping_address_snapshot={'full_name': 'Buyer 2', 'city': 'Mumbai', 'pincode': '400001'},
            subtotal=Decimal('499.00'),
            shipping_fee=Decimal('0.00'),
            total_amount=Decimal('499.00'),
            status='PENDING_PAYMENT',
            payment_status='UNPAID'
        )

    def test_upi_payment_submission_workflow(self):
        self.client.login(username='buyer2', password='Password123!')
        
        # Submit UTR
        response = self.client.post(reverse('payments:submit_payment', kwargs={'order_number': self.order.order_number}), {
            'utr_number': '123456789012',
            'payer_name': 'Karan Malhotra',
            'payer_upi_id': 'karan@okhdfcbank'
        })
        self.assertEqual(response.status_code, 302)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'PAYMENT_VERIFICATION')
        self.assertEqual(self.order.payment_status, 'SUBMITTED')

        payment = Payment.objects.filter(order=self.order).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.utr_number, '123456789012')
        self.assertEqual(payment.status, 'PENDING')

    def test_admin_manual_payment_approval(self):
        payment = Payment.objects.create(
            order=self.order,
            amount=self.order.total_amount,
            utr_number='UTR888999111',
            status='PENDING'
        )
        
        # Admin approves payment
        payment.approve(admin_user=self.admin, notes="Bank transaction confirmed on statement")
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'PAYMENT_VERIFIED')
        self.assertEqual(self.order.payment_status, 'VERIFIED')
        self.assertEqual(payment.status, 'VERIFIED')
        self.assertEqual(payment.verified_by, self.admin)

    def test_duplicate_verified_utr_prevention(self):
        # Create an already verified payment with UTR "VERIFIED_UTR_123"
        Payment.objects.create(
            order=self.order,
            amount=self.order.total_amount,
            utr_number='VERIFIED_UTR_123',
            status='VERIFIED'
        )

        # Another customer creates order and tries to reuse the same UTR
        other_user = User.objects.create_user(username='fraudster', email='fraud@test.com', password='Password123!')
        other_order = Order.objects.create(
            user=other_user,
            shipping_address_snapshot={'full_name': 'Fraud', 'city': 'Delhi', 'pincode': '110001'},
            subtotal=Decimal('499.00'),
            total_amount=Decimal('499.00')
        )

        self.client.login(username='fraudster', password='Password123!')
        response = self.client.post(reverse('payments:submit_payment', kwargs={'order_number': other_order.order_number}), {
            'utr_number': 'VERIFIED_UTR_123'
        })
        self.assertEqual(response.status_code, 302)
        
        # Payment should NOT be created for this order
        self.assertFalse(Payment.objects.filter(order=other_order, utr_number='VERIFIED_UTR_123').exists())

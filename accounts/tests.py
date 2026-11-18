from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, CustomerAddress
from orders.models import Order


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testcustomer',
            email='customer@example.com',
            password='Password123!',
            first_name='Rahul',
            last_name='Sharma',
            phone_number='9876543210'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='Password123!',
            first_name='Priya',
            last_name='Patel'
        )

    def test_customer_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'first_name': 'Aman',
            'last_name': 'Verma',
            'email': 'aman@example.com',
            'phone_number': '9988776655',
            'password': 'SecurePassword123',
            'password_confirm': 'SecurePassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='aman@example.com').exists())

    def test_customer_login(self):
        response = self.client.post(reverse('accounts:login'), {
            'login_id': 'customer@example.com',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        # Verify authenticated
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_address_management(self):
        self.client.login(username='testcustomer', password='Password123!')
        
        # Add Address
        response = self.client.post(reverse('accounts:address_create'), {
            'full_name': 'Rahul Sharma',
            'phone_number': '9876543210',
            'address_line_1': 'Plot 42, Civil Lines',
            'city': 'Jaipur',
            'state': 'Rajasthan',
            'pincode': '302006',
            'address_type': 'HOME',
        })
        self.assertEqual(response.status_code, 302)
        address = CustomerAddress.objects.filter(user=self.user).first()
        self.assertIsNotNone(address)
        self.assertEqual(address.city, 'Jaipur')
        self.assertTrue(address.is_default)

    def test_unauthorized_order_access_prevention(self):
        """Customers must ONLY be able to access their own orders!"""
        order = Order.objects.create(
            user=self.user,
            shipping_address_snapshot={'full_name': 'Rahul', 'city': 'Jaipur', 'pincode': '302006'},
            subtotal=499,
            shipping_fee=0,
            total_amount=499,
            status='PENDING_PAYMENT'
        )

        # Login as other_user and attempt to access self.user's order
        self.client.login(username='otheruser', password='Password123!')
        response = self.client.get(reverse('accounts:order_detail', kwargs={'order_number': order.order_number}))
        self.assertEqual(response.status_code, 403)

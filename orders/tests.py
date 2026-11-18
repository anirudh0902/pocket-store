from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, CustomerAddress
from products.models import Category, Product
from orders.models import Cart, CartItem, Order, OrderItem


class OrdersTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='buyer',
            email='buyer@pocket.in',
            password='Password123!',
            first_name='Karan'
        )
        self.category = Category.objects.create(name="Tees")
        self.product = Product.objects.create(
            category=self.category,
            name="Pocket Tee",
            description="Cotton tee",
            selling_price=Decimal('299.00'),
            source_cost=Decimal('120.00'),
            stock_quantity=20,
            is_active=True
        )

    def test_cart_functionality_and_shipping_calculation(self):
        self.client.login(username='buyer', password='Password123!')
        
        # Add 1 item (Subtotal = ₹299 < ₹499 free threshold -> Shipping = ₹49)
        response = self.client.post(reverse('orders:cart_add', kwargs={'product_id': self.product.id}), {
            'quantity': 1
        })
        self.assertEqual(response.status_code, 302)

        cart = Cart.objects.filter(user=self.user).first()
        self.assertIsNotNone(cart)
        self.assertEqual(cart.subtotal, Decimal('299.00'))
        self.assertEqual(cart.shipping_charge, Decimal('49.00'))
        self.assertEqual(cart.grand_total, Decimal('348.00'))

        # Add second unit (Subtotal = ₹598 >= ₹499 free threshold -> Shipping = ₹0)
        self.client.post(reverse('orders:cart_add', kwargs={'product_id': self.product.id}), {
            'quantity': 1
        })
        cart.refresh_from_db()
        self.assertEqual(cart.subtotal, Decimal('598.00'))
        self.assertEqual(cart.shipping_charge, Decimal('0.00'))
        self.assertEqual(cart.grand_total, Decimal('598.00'))

    def test_checkout_and_order_creation(self):
        self.client.login(username='buyer', password='Password123!')
        
        # Add to cart
        self.client.post(reverse('orders:cart_add', kwargs={'product_id': self.product.id}), {'quantity': 2})

        # Checkout
        response = self.client.post(reverse('orders:checkout'), {
            'full_name': 'Karan Malhotra',
            'phone_number': '9812345678',
            'address_line_1': 'House 12, Park Street',
            'city': 'Delhi',
            'state': 'Delhi',
            'pincode': '110001',
            'save_address': 'on'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify order created
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.subtotal, Decimal('598.00'))
        self.assertEqual(order.total_amount, Decimal('598.00'))
        self.assertEqual(order.total_supplier_cost, Decimal('240.00'))
        self.assertEqual(order.status, 'PENDING_PAYMENT')
        self.assertEqual(order.payment_status, 'UNPAID')
        self.assertEqual(order.items.count(), 1)
        
        # Cart should now be empty
        cart = Cart.objects.filter(user=self.user).first()
        self.assertEqual(cart.items.count(), 0)

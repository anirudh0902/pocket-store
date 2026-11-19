from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Category, Product, ProductVariant
from orders.models import Cart, Order
from payments.models import SiteConfiguration, Payment
from admin_dashboard.models import Supplier

User = get_user_model()


class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.config = SiteConfiguration.get_solo()
        self.config.upi_id = "pocketfashion@upi"
        self.config.account_display_name = "POCKET FASHION STORE"
        self.config.free_shipping_threshold = Decimal('499.00')
        self.config.standard_shipping_charge = Decimal('49.00')
        self.config.save()

        self.supplier = Supplier.objects.create(
            name="Confidential Supplier Tirupur",
            platform="MANUFACTURER",
            contact_person="Internal Sourcing Manager",
            phone="+91 99999 88888",
            internal_notes="Secret wholesale pricing notes - must never be visible to public"
        )

        self.category = Category.objects.create(
            name="Oversized T-shirts",
            slug="oversized-t-shirts",
            description="Premium streetwear",
            display_order=1,
            is_active=True
        )

        self.product = Product.objects.create(
            name="POCKET 240 GSM Acid Wash Oversized Tee",
            slug="pocket-240-gsm-acid-wash-oversized-tee",
            category=self.category,
            description="Heavyweight 240 GSM drop shoulder tee",
            specifications="Fabric: 100% Cotton",
            selling_price=Decimal('599.00'),
            original_price=Decimal('999.00'),
            source_cost=Decimal('250.00'),  # INTERNAL ONLY
            stock_quantity=50,
            supplier=self.supplier,  # INTERNAL ONLY
            is_active=True,
            is_trending=True,
            is_bestseller=True
        )

        self.variant = ProductVariant.objects.create(
            product=self.product,
            size="L",
            color="Charcoal Black",
            color_code="#1F2937",
            stock_quantity=20,
            is_active=True
        )

    def test_health_check_endpoints(self):
        """Verify both /health/ and /api/v1/health/ return 200 and healthy status."""
        resp1 = self.client.get('/health/')
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp1.json()['status'], 'healthy')
        self.assertEqual(resp1.json()['database'], 'connected')

        resp2 = self.client.get('/api/v1/health/')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()['status'], 'healthy')

    def test_categories_api(self):
        """Verify category list and detail endpoints."""
        resp = self.client.get('/api/v1/categories/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0]['slug'], 'oversized-t-shirts')
        self.assertEqual(data[0]['products_count'], 1)

        resp_detail = self.client.get(f'/api/v1/categories/{self.category.slug}/')
        self.assertEqual(resp_detail.status_code, 200)
        self.assertEqual(resp_detail.json()['name'], 'Oversized T-shirts')

    def test_products_api_and_supplier_privacy_shield(self):
        """Verify product list and detail and ENSURE supplier costs and names are NEVER leaked."""
        resp = self.client.get('/api/v1/products/')
        self.assertEqual(resp.status_code, 200)
        results = resp.json()['results']
        self.assertTrue(len(results) >= 1)
        first = results[0]
        self.assertEqual(first['slug'], self.product.slug)

        # STRICT PRIVACY ASSERTIONS
        self.assertNotIn('source_cost', first)
        self.assertNotIn('supplier', first)
        self.assertNotIn('internal_notes', first)
        self.assertNotIn('estimated_profit', first)

        # Detail endpoint
        resp_detail = self.client.get(f'/api/v1/products/{self.product.slug}/')
        self.assertEqual(resp_detail.status_code, 200)
        detail_data = resp_detail.json()
        self.assertEqual(detail_data['name'], self.product.name)
        self.assertEqual(len(detail_data['variants']), 1)
        self.assertEqual(detail_data['variants'][0]['size'], 'L')

        # STRICT PRIVACY ASSERTIONS ON DETAIL
        self.assertNotIn('source_cost', detail_data)
        self.assertNotIn('supplier', detail_data)
        self.assertNotIn('internal_notes', detail_data)
        self.assertNotIn('estimated_profit', detail_data)

    def test_cart_workflow(self):
        """Verify full guest cart workflow: add, view, update, delete."""
        # 1. Add item to cart
        add_resp = self.client.post('/api/v1/cart/add/', {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 2
        }, content_type='application/json')
        self.assertEqual(add_resp.status_code, 200)
        cart_data = add_resp.json()
        self.assertEqual(cart_data['total_items'], 2)
        self.assertEqual(Decimal(str(cart_data['subtotal'])), Decimal('1198.00'))
        self.assertTrue(cart_data['qualifies_for_free_shipping'])
        self.assertEqual(Decimal(str(cart_data['shipping_fee'])), Decimal('0.00'))

        item_id = cart_data['items'][0]['id']

        # 2. Update quantity
        update_resp = self.client.patch(f'/api/v1/cart/update/{item_id}/', {
            'quantity': 3
        }, content_type='application/json')
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json()['total_items'], 3)

        # 3. View cart
        get_resp = self.client.get('/api/v1/cart/')
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()['total_items'], 3)

        # 4. Remove item
        del_resp = self.client.delete(f'/api/v1/cart/remove/{item_id}/')
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(del_resp.json()['total_items'], 0)

    def test_checkout_and_upi_payment_submission_workflow(self):
        """Verify complete checkout, UPI intent generation, and UTR reference submission."""
        # Add product to cart
        self.client.post('/api/v1/cart/add/', {
            'product_id': self.product.id,
            'variant_id': self.variant.id,
            'quantity': 1
        }, content_type='application/json')

        # Checkout
        checkout_resp = self.client.post('/api/v1/orders/checkout/', {
            'full_name': 'Rahul Sharma',
            'phone': '9876543210',
            'street_address': 'Flat 402, Green Avenue, MG Road',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'postal_code': '560001',
            'landmark': 'Near Metro Station'
        }, content_type='application/json')

        self.assertEqual(checkout_resp.status_code, 201)
        data = checkout_resp.json()
        order_number = data['order']['order_number']
        self.assertEqual(data['order']['status'], 'PENDING_PAYMENT')
        self.assertEqual(data['order']['payment_status'], 'UNPAID')
        self.assertTrue(order_number.startswith('PKT-'))

        # Fetch UPI Details
        upi_resp = self.client.get(f'/api/v1/payments/upi-details/?order_number={order_number}')
        self.assertEqual(upi_resp.status_code, 200)
        upi_data = upi_resp.json()
        self.assertEqual(upi_data['upi_id'], 'pocketfashion@upi')
        self.assertTrue('upi://pay?' in upi_data['upi_intent_url'])

        # Submit UTR
        utr_resp = self.client.post('/api/v1/payments/submit-utr/', {
            'order_number': order_number,
            'utr_number': 'SBIN202611198899',
            'payer_name': 'Rahul Sharma',
            'payer_phone': '9876543210'
        }, content_type='application/json')

        self.assertEqual(utr_resp.status_code, 200)
        self.assertEqual(utr_resp.json()['status'], 'PAYMENT_UNDER_VERIFICATION')

        # Verify Order state in Database
        order = Order.objects.get(order_number=order_number)
        self.assertEqual(order.status, 'PAYMENT_UNDER_VERIFICATION')
        # Crucial security business rule check: payment must NOT be automatically confirmed
        self.assertNotEqual(order.status, 'CONFIRMED')
        self.assertNotEqual(order.payment_status, 'PAID')

        # Track order via public guest tracking endpoint
        track_resp = self.client.get(f'/api/v1/orders/track/?order_number={order_number}&phone=9876543210')
        self.assertEqual(track_resp.status_code, 200)
        self.assertEqual(track_resp.json()['order_number'], order_number)
        self.assertEqual(track_resp.json()['status'], 'PAYMENT_UNDER_VERIFICATION')

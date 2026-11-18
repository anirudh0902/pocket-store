from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from products.models import Category, Product, ProductVariant


class ProductsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Men's Wear", slug="mens-wear")
        self.product = Product.objects.create(
            category=self.category,
            name="Classic Denim Jacket",
            description="High quality durable denim jacket",
            selling_price=Decimal('899.00'),
            original_price=Decimal('1499.00'),
            source_cost=Decimal('450.00'),
            stock_quantity=15,
            is_active=True,
            is_trending=True,
            is_bestseller=True
        )

    def test_product_slug_and_discount_calculation(self):
        self.assertTrue(self.product.slug.startswith('classic-denim-jacket'))
        self.assertTrue(self.product.has_discount)
        self.assertEqual(self.product.discount_percentage, 40)
        self.assertEqual(self.product.internal_unit_margin, Decimal('449.00'))

    def test_search_and_category_filtering(self):
        # Search match
        response = self.client.get(reverse('products:product_list') + '?q=Denim')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Classic Denim Jacket")

        # Category match
        response = self.client.get(reverse('products:category_products', kwargs={'slug': 'mens-wear'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Classic Denim Jacket")

        # Price filter
        response = self.client.get(reverse('products:product_list') + '?min_price=1000')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Classic Denim Jacket")

    def test_product_detail_page(self):
        response = self.client.get(reverse('products:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Classic Denim Jacket")
        self.assertContains(response, "₹899")
        # Ensure internal supplier cost is NOT exposed on customer-facing page
        self.assertNotContains(response, "₹450")
        self.assertNotContains(response, "Supplier Purchase Cost")

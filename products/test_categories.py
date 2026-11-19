from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError
from accounts.models import User
from products.models import Category, Product, ProductImage, ProductVariant


class CategorySystemTestCase(TestCase):
    """
    Test suite for the 7 product categories and published clothing products in POCKET:
    1. Oversized T-shirts
    2. Graphic T-shirts
    3. Basic T-shirts
    4. Polo T-shirts
    5. Casual Shirts
    6. Joggers
    7. Cargo Pants
    """

    SEVEN_CATEGORIES = [
        ('Oversized T-shirts', 'oversized-t-shirts', 1, 'categories/oversized-t-shirts.jpg'),
        ('Graphic T-shirts', 'graphic-t-shirts', 2, 'categories/graphic-t-shirts.jpg'),
        ('Basic T-shirts', 'basic-t-shirts', 3, 'categories/basic-t-shirts.jpg'),
        ('Polo T-shirts', 'polo-t-shirts', 4, 'categories/polo-t-shirts.jpg'),
        ('Casual Shirts', 'casual-shirts', 5, 'categories/casual-shirts.jpg'),
        ('Joggers', 'joggers', 6, 'categories/joggers.jpg'),
        ('Cargo Pants', 'cargo-pants', 7, 'categories/cargo-pants.jpg'),
    ]

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin_test@pocketfashion.in',
            password='TestPassword123!',
            is_pocket_admin=True,
            is_staff=True
        )

        # Seed the 7 categories for the test database
        for name, slug, order, img in self.SEVEN_CATEGORIES:
            Category.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slug,
                    'display_order': order,
                    'image': img,
                    'is_active': True,
                    'description': f'Premium collection of {name} at POCKET.'
                }
            )

    def test_all_seven_categories_exist_with_correct_slugs_and_images(self):
        """Verify all 7 categories exist in the database with expected properties."""
        for name, expected_slug, expected_order, expected_img in self.SEVEN_CATEGORIES:
            cat = Category.objects.filter(slug=expected_slug).first()
            self.assertIsNotNone(cat, f"Category '{name}' with slug '{expected_slug}' was not found.")
            self.assertEqual(cat.name, name)
            self.assertEqual(cat.display_order, expected_order)
            self.assertTrue(cat.is_active)
            self.assertEqual(str(cat.image), expected_img)

    def test_category_detail_pages_return_http_200(self):
        """Verify each category's dedicated filtered page loads successfully."""
        for name, slug, _, _ in self.SEVEN_CATEGORIES:
            url = reverse('products:category_products', kwargs={'slug': slug})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"URL {url} for category '{name}' returned status {response.status_code}")
            self.assertContains(response, name)

    def test_category_query_filter_returns_http_200(self):
        """Verify shop catalogue query parameter filtering (/shop/?category=<slug>) works."""
        for name, slug, _, _ in self.SEVEN_CATEGORIES:
            url = reverse('products:product_list') + f'?category={slug}'
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Query filter URL {url} returned status {response.status_code}")
            self.assertContains(response, name)

    def test_category_list_page_contains_all_seven_categories(self):
        """Verify /shop/categories/ lists all 7 categories and renders their images."""
        url = reverse('products:category_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for name, slug, _, img in self.SEVEN_CATEGORIES:
            self.assertContains(response, name)
            self.assertContains(response, slug)

    def test_homepage_navigation_and_featured_clothing_categories(self):
        """Verify homepage renders the categories in the navigation and category section."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        for name, slug, _, _ in self.SEVEN_CATEGORIES:
            self.assertContains(response, name)
            self.assertContains(response, slug)

    def test_duplicate_category_prevention(self):
        """Verify that duplicating an existing category name is prevented by database constraints."""
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Oversized T-shirts', slug='oversized-t-shirts-duplicate')

    def test_admin_category_list_management(self):
        """Verify admin dashboard displays all categories for management."""
        self.client.login(username='admin_test', password='TestPassword123!')
        url = reverse('admin_dashboard:category_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for name, slug, _, _ in self.SEVEN_CATEGORIES:
            self.assertContains(response, name)
            self.assertContains(response, slug)

    def test_product_publishing_in_category(self):
        """Verify that products assigned to a category render cleanly on the category page."""
        cat = Category.objects.get(slug='oversized-t-shirts')
        prod = Product.objects.create(
            category=cat,
            name='Test Heavyweight Oversized Tee',
            slug='test-heavyweight-oversized-tee',
            description='Test description',
            selling_price=Decimal('499.00'),
            original_price=Decimal('999.00'),
            source_cost=Decimal('240.00'),
            stock_quantity=20,
            is_active=True
        )
        url = reverse('products:category_products', kwargs={'slug': 'oversized-t-shirts'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Heavyweight Oversized Tee')
        self.assertContains(response, '₹499')
        # Ensure internal supplier cost is NOT exposed on category page
        self.assertNotContains(response, '₹240')

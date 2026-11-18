from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from decimal import Decimal


class Category(models.Model):
    """
    Product categories (e.g., Men's Wear, Women's Wear, Accessories, Footwear).
    """
    name = models.CharField(max_length=120, unique=True, verbose_name="Category Name")
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Category Description")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Category Banner/Image")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category_products', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    @property
    def active_products_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """
    Main product catalog model.
    Contains customer-visible selling details as well as internal supplier/cost fields.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Category"
    )
    name = models.CharField(max_length=255, verbose_name="Product Name")
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField(verbose_name="Detailed Description")
    specifications = models.TextField(
        blank=True,
        help_text="Line-separated specifications (e.g. Fabric: 100% Cotton | Pattern: Solid | Fit: Slim Fit)",
        verbose_name="Product Specifications"
    )
    
    # Pricing
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Selling Price (₹)",
        help_text="Customer-facing retail price"
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Original MRP (₹)",
        help_text="Genuine MRP if applicable (used for genuine discount display)"
    )

    # Internal Business & Supplier Information (STRICTLY PRIVATE)
    source_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Supplier Purchase Cost (₹)",
        help_text="Internal cost paid to supplier/vendor. NEVER show to customer."
    )
    supplier = models.ForeignKey(
        'admin_dashboard.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Supplier (Internal)",
        help_text="Internal procurement source"
    )
    supplier_sku_or_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Supplier SKU / Listing Link (Internal)"
    )

    # Inventory & Status
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Total Available Stock")
    is_active = models.BooleanField(default=True, verbose_name="Is Active / Published")
    is_featured = models.BooleanField(default=False, verbose_name="Featured Product")
    is_bestseller = models.BooleanField(default=False, verbose_name="Best Seller")
    is_trending = models.BooleanField(default=False, verbose_name="Trending Now")

    # Delivery & Return Policy Info (Genuine & clear)
    delivery_info = models.TextField(
        default="Free delivery on orders above ₹499. Dispatched within 24-48 hours. Delivered in 4-7 business days across India.",
        verbose_name="Delivery Information"
    )
    return_policy_info = models.TextField(
        default="7-Day replacement or return available in case of defective, wrong, or damaged items received.",
        verbose_name="Return / Exchange Policy"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @property
    def primary_image(self):
        first_img = self.images.filter(is_primary=True).first()
        if not first_img:
            first_img = self.images.first()
        return first_img

    @property
    def has_discount(self):
        return bool(self.original_price and self.original_price > self.selling_price)

    @property
    def discount_percentage(self):
        if self.has_discount and self.original_price:
            diff = self.original_price - self.selling_price
            return int((diff / self.original_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        # Either base product has stock or variants have stock
        if self.stock_quantity > 0:
            return True
        return self.variants.filter(is_active=True, stock_quantity__gt=0).exists()

    @property
    def internal_unit_margin(self):
        """Internal calculation: unit margin before shipping & overhead."""
        return self.selling_price - self.source_cost

    @property
    def average_rating(self):
        approved_reviews = self.reviews.filter(is_approved=True)
        if approved_reviews.exists():
            avg = approved_reviews.aggregate(models.Avg('rating'))['rating__avg']
            return round(avg, 1) if avg else None
        return None

    @property
    def reviews_count(self):
        return self.reviews.filter(is_approved=True).count()

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """
    Multiple image support for each product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', verbose_name="Product Photo")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Alt Text")
    is_primary = models.BooleanField(default=False, verbose_name="Primary / Main Image")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Sort Order")

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ['display_order', '-is_primary', 'id']

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name} ({'Primary' if self.is_primary else 'Gallery'})"


class ProductVariant(models.Model):
    """
    Sizes, Colors, and variant-specific inventory management.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=30, blank=True, verbose_name="Size (e.g. S, M, L, XL, XXL, 32, Free Size)")
    color = models.CharField(max_length=40, blank=True, verbose_name="Color Name (e.g. Navy Blue, Rust Orange)")
    color_code = models.CharField(max_length=10, blank=True, help_text="Hex code, e.g. #0B162C", verbose_name="Color Hex Code")
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Extra Price (₹)")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Variant Stock")
    sku = models.CharField(max_length=80, blank=True, verbose_name="SKU Code")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
        ordering = ['size', 'color']

    @property
    def final_price(self):
        return self.product.selling_price + self.additional_price

    def __str__(self):
        parts = []
        if self.size:
            parts.append(f"Size: {self.size}")
        if self.color:
            parts.append(f"Color: {self.color}")
        desc = ", ".join(parts) if parts else "Default"
        return f"{self.product.name} - {desc} (Stock: {self.stock_quantity})"


class ProductReview(models.Model):
    """
    Genuine customer reviews with verified purchase check.
    Only approved genuine reviews are displayed on customer-facing pages.
    """
    RATING_CHOICES = [(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Rating")
    review_text = models.TextField(blank=True, verbose_name="Customer Review")
    is_verified_purchase = models.BooleanField(default=False, verbose_name="Verified Purchase")
    is_approved = models.BooleanField(default=True, verbose_name="Approved for Display")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.rating}★ on {self.product.name}"

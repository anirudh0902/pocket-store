import re
from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth import get_user_model
from products.models import Category, Product, ProductImage, ProductVariant, ProductReview
from orders.models import Cart, CartItem, Order, OrderItem, OrderStatusHistory, Wishlist, WishlistItem
from payments.models import SiteConfiguration, Payment
from accounts.models import CustomerAddress

User = get_user_model()


# ----------------------------------------------------
# 1. CATEGORY & PRODUCT SERIALIZERS (PUBLIC)
# ----------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'image_url',
            'display_order',
            'products_count',
        ]

    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'is_primary', 'display_order']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'size',
            'color',
            'color_code',
            'stock_quantity',
            'is_in_stock',
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = ['id', 'user_name', 'rating', 'title', 'comment', 'created_at']

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class ProductListSerializer(serializers.ModelSerializer):
    """Card format for catalogs, search, trending, and category listing grids."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    primary_image_url = serializers.SerializerMethodField()
    has_discount = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'category_name',
            'category_slug',
            'selling_price',
            'original_price',
            'has_discount',
            'discount_percentage',
            'primary_image_url',
            'is_in_stock',
            'is_trending',
            'is_bestseller',
            'average_rating',
            'reviews_count',
        ]

    def get_primary_image_url(self, obj):
        pi = obj.primary_image
        if pi and pi.image:
            request = self.context.get('request')
            return request.build_absolute_uri(pi.image.url) if request else pi.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full detail format for product detail page, gallery, specifications, and variants."""
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = serializers.SerializerMethodField()
    reviews = ProductReviewSerializer(many=True, read_only=True)
    has_discount = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

    # Strictly excluded for business privacy: source_cost, supplier, internal_notes, estimated_profit
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'category',
            'description',
            'specifications',
            'selling_price',
            'original_price',
            'has_discount',
            'discount_percentage',
            'is_in_stock',
            'stock_quantity',
            'images',
            'variants',
            'reviews',
            'is_trending',
            'is_bestseller',
            'average_rating',
            'reviews_count',
            'created_at',
        ]

    def get_variants(self, obj):
        active_variants = obj.variants.filter(is_active=True).order_by('size', 'color')
        return ProductVariantSerializer(active_variants, many=True, context=self.context).data


# ----------------------------------------------------
# 2. CART SERIALIZERS
# ----------------------------------------------------

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'variant', 'quantity', 'total_price', 'created_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(source='total_items_count', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    shipping_fee = serializers.SerializerMethodField()
    free_shipping_threshold = serializers.SerializerMethodField()
    free_shipping_remaining = serializers.SerializerMethodField()
    qualifies_for_free_shipping = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'total_items',
            'subtotal',
            'shipping_fee',
            'free_shipping_threshold',
            'free_shipping_remaining',
            'qualifies_for_free_shipping',
            'total_amount',
            'items',
            'updated_at',
        ]

    def _get_config(self):
        return SiteConfiguration.get_solo()

    def get_shipping_fee(self, obj):
        config = self._get_config()
        if obj.subtotal >= config.free_shipping_threshold or obj.total_items_count == 0:
            return Decimal('0.00')
        return config.standard_shipping_charge

    def get_free_shipping_threshold(self, obj):
        return self._get_config().free_shipping_threshold

    def get_free_shipping_remaining(self, obj):
        config = self._get_config()
        diff = config.free_shipping_threshold - obj.subtotal
        return max(Decimal('0.00'), diff)

    def get_qualifies_for_free_shipping(self, obj):
        config = self._get_config()
        return obj.subtotal >= config.free_shipping_threshold

    def get_total_amount(self, obj):
        shipping = self.get_shipping_fee(obj)
        return obj.subtotal + shipping


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate(self, attrs):
        product_id = attrs.get('product_id')
        variant_id = attrs.get('variant_id')
        qty = attrs.get('quantity', 1)

        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            raise serializers.ValidationError({"product_id": "Invalid or inactive product."})

        if not product.is_in_stock:
            raise serializers.ValidationError({"product": "This product is currently out of stock."})

        variant = None
        if variant_id:
            variant = ProductVariant.objects.filter(id=variant_id, product=product, is_active=True).first()
            if not variant:
                raise serializers.ValidationError({"variant_id": "Selected variant does not exist for this product."})
            if variant.stock_quantity < qty:
                raise serializers.ValidationError({"quantity": f"Only {variant.stock_quantity} pieces available in this variant."})
        else:
            # If product has required variants, ensure user selects one
            if product.variants.filter(is_active=True).exists():
                raise serializers.ValidationError({"variant_id": "Please select a size/color variant for this product."})
            if product.stock_quantity < qty:
                raise serializers.ValidationError({"quantity": f"Only {product.stock_quantity} items available."})

        attrs['product_obj'] = product
        attrs['variant_obj'] = variant
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


# ----------------------------------------------------
# 3. ORDER & CHECKOUT SERIALIZERS
# ----------------------------------------------------

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product_name',
            'variant_details',
            'unit_price',
            'quantity',
            'total_price',
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ['status', 'comment', 'created_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    # Strictly excluded: total_supplier_cost, supplier, supplier_order_reference, estimated_profit, internal_notes
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'status_display',
            'payment_status',
            'payment_status_display',
            'subtotal',
            'shipping_fee',
            'total_amount',
            'shipping_address_snapshot',
            'customer_notes',
            'items',
            'status_history',
            'created_at',
            'updated_at',
        ]


class CheckoutSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20)
    street_address = serializers.CharField(max_length=255)
    apartment_suite = serializers.CharField(max_length=100, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)
    landmark = serializers.CharField(max_length=150, required=False, allow_blank=True)
    customer_notes = serializers.CharField(required=False, allow_blank=True)

    def validate_phone(self, value):
        cleaned = re.sub(r'[\s\-\(\)]', '', value)
        if len(cleaned) < 10:
            raise serializers.ValidationError("Please provide a valid 10-digit mobile number.")
        return cleaned

    def validate_postal_code(self, value):
        cleaned = re.sub(r'\s+', '', value)
        if len(cleaned) < 5:
            raise serializers.ValidationError("Please provide a valid postal code / PIN code.")
        return cleaned


# ----------------------------------------------------
# 4. PAYMENT SERIALIZERS (UPI & MANUAL VERIFICATION)
# ----------------------------------------------------

class UPIDetailsSerializer(serializers.Serializer):
    order_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    upi_id = serializers.CharField()
    account_display_name = serializers.CharField()
    upi_intent_url = serializers.CharField()
    payment_instructions = serializers.CharField()


class SubmitUTRSerializer(serializers.Serializer):
    order_number = serializers.CharField(max_length=64)
    utr_number = serializers.CharField(max_length=50)
    payer_name = serializers.CharField(max_length=150)
    payer_phone = serializers.CharField(max_length=20)

    def validate_utr_number(self, value):
        cleaned = value.strip().upper()
        if len(cleaned) < 8 or len(cleaned) > 25:
            raise serializers.ValidationError("UTR / Bank Reference number should be between 8 and 25 characters.")
        if not re.match(r'^[A-Z0-9]+$', cleaned):
            raise serializers.ValidationError("UTR number should only contain alphanumeric characters.")
        return cleaned

    def validate_order_number(self, value):
        order = Order.objects.filter(order_number=value).first()
        if not order:
            raise serializers.ValidationError("Order not found.")
        return value


# ----------------------------------------------------
# 5. USER AUTH & PROFILE SERIALIZERS
# ----------------------------------------------------

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'password']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return value.lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username') or validated_data.get('email'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            password=validated_data.get('password'),
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'date_joined']
        read_only_fields = ['id', 'username', 'email', 'date_joined']


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            'id',
            'full_name',
            'phone',
            'street_address',
            'apartment_suite',
            'city',
            'state',
            'postal_code',
            'landmark',
            'is_default',
            'address_type',
        ]

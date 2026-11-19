import uuid
from decimal import Decimal
from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from products.models import Category, Product, ProductVariant
from orders.models import Cart, CartItem, Order, OrderItem, OrderStatusHistory
from payments.models import SiteConfiguration, Payment
from accounts.models import CustomerAddress

from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
    CheckoutSerializer,
    OrderDetailSerializer,
    UPIDetailsSerializer,
    SubmitUTRSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    CustomerAddressSerializer,
)

User = get_user_model()


# ----------------------------------------------------
# 1. HEALTH CHECK ENDPOINT
# ----------------------------------------------------

class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        db_status = "connected"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            db_status = f"error: {str(e)}"

        cache_status = "connected"
        try:
            cache.set("pocket_health_ping", "ok", 10)
            val = cache.get("pocket_health_ping")
            if val != "ok":
                cache_status = "fallback"
        except Exception:
            cache_status = "offline"

        is_healthy = db_status == "connected"
        status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response({
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "POCKET Production API",
            "version": "1.0.0",
            "database": db_status,
            "cache": cache_status,
            "timestamp": timezone.now().isoformat(),
        }, status=status_code)


# ----------------------------------------------------
# 2. CATEGORIES API
# ----------------------------------------------------

class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cache_key = "pocket_api_categories_list"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        cache.set(cache_key, serializer.data, 900)  # 15 minutes TTL
        return Response(serializer.data)


class CategoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        category = Category.objects.filter(slug=slug, is_active=True).first()
        if not category:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)


# ----------------------------------------------------
# 3. PRODUCTS API
# ----------------------------------------------------

class StandardProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 48


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')

        # Filter by category slug
        category_slug = request.query_params.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        # Keyword search across title, description, and specifications
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(specifications__icontains=search)
            )

        # Filter by promotional badge
        badge_filter = request.query_params.get('filter')
        if badge_filter == 'trending':
            qs = qs.filter(is_trending=True)
        elif badge_filter == 'bestseller':
            qs = qs.filter(is_bestseller=True)

        # Price range filtering
        min_price = request.query_params.get('min_price')
        if min_price:
            try:
                qs = qs.filter(selling_price__gte=Decimal(min_price))
            except Exception:
                pass

        max_price = request.query_params.get('max_price')
        if max_price:
            try:
                qs = qs.filter(selling_price__lte=Decimal(max_price))
            except Exception:
                pass

        # Sorting
        sort = request.query_params.get('sort', 'popular')
        if sort == 'price_asc':
            qs = qs.order_by('selling_price')
        elif sort == 'price_desc':
            qs = qs.order_by('-selling_price')
        elif sort == 'newest':
            qs = qs.order_by('-created_at')
        else:
            # Popular / Default: Best sellers first, then display order
            qs = qs.order_by('-is_bestseller', '-is_trending', 'category__display_order', 'id')

        paginator = StandardProductPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ProductListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        product = Product.objects.filter(slug=slug, is_active=True).select_related('category').prefetch_related('images', 'variants', 'reviews').first()
        if not product:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductDetailSerializer(product, context={'request': request})
        return Response(serializer.data)


# ----------------------------------------------------
# 4. CART API (Supports Auth + Guest Session Token)
# ----------------------------------------------------

def _resolve_cart(request):
    """Resolves or creates a database Cart instance for either authenticated user or guest session token."""
    session_key = request.headers.get('X-Session-Key') or request.session.session_key
    if not session_key and not request.user.is_authenticated:
        if not request.session.exists(request.session.session_key):
            request.session.create()
        session_key = request.session.session_key

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # If there's a guest cart with session_key, merge it
        if session_key:
            guest_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            if guest_cart and guest_cart != cart:
                for item in guest_cart.items.all():
                    existing = cart.items.filter(product=item.product, variant=item.variant).first()
                    if existing:
                        existing.quantity += item.quantity
                        existing.save()
                    else:
                        item.cart = cart
                        item.save()
                guest_cart.delete()
        return cart, session_key
    else:
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
        return cart, session_key


class CartDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cart, session_key = _resolve_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        resp = Response(serializer.data)
        if session_key:
            resp['X-Session-Key'] = session_key
        return resp


class AddToCartView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, session_key = _resolve_cart(request)
        product = serializer.validated_data['product_obj']
        variant = serializer.validated_data.get('variant_obj')
        qty = serializer.validated_data.get('quantity', 1)

        with transaction.atomic():
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=variant,
                defaults={'quantity': qty}
            )
            if not created:
                cart_item.quantity += qty
                cart_item.save()

        cart_data = CartSerializer(cart, context={'request': request}).data
        resp = Response(cart_data, status=status.HTTP_200_OK)
        if session_key:
            resp['X-Session-Key'] = session_key
        return resp


class UpdateCartItemView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, _ = _resolve_cart(request)
        item = cart.items.filter(id=item_id).first()
        if not item:
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        new_qty = serializer.validated_data['quantity']
        # Stock check
        if item.variant and item.variant.stock_quantity < new_qty:
            return Response({"detail": f"Only {item.variant.stock_quantity} available."}, status=status.HTTP_400_BAD_REQUEST)
        elif not item.variant and item.product.stock_quantity < new_qty:
            return Response({"detail": f"Only {item.product.stock_quantity} available."}, status=status.HTTP_400_BAD_REQUEST)

        item.quantity = new_qty
        item.save()
        return Response(CartSerializer(cart, context={'request': request}).data)


class RemoveCartItemView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, item_id):
        cart, _ = _resolve_cart(request)
        item = cart.items.filter(id=item_id).first()
        if not item:
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(CartSerializer(cart, context={'request': request}).data)


class ClearCartView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        cart, _ = _resolve_cart(request)
        cart.items.all().delete()
        return Response(CartSerializer(cart, context={'request': request}).data)


# ----------------------------------------------------
# 5. CHECKOUT & ORDERS API
# ----------------------------------------------------

class CheckoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, _ = _resolve_cart(request)
        if cart.items.count() == 0:
            return Response({"detail": "Cannot checkout with an empty cart."}, status=status.HTTP_400_BAD_REQUEST)

        config = SiteConfiguration.get_solo()
        subtotal = cart.subtotal
        shipping_fee = Decimal('0.00') if subtotal >= config.free_shipping_threshold else config.standard_shipping_charge
        total_amount = subtotal + shipping_fee

        # Build address snapshot JSON string
        address_snapshot = (
            f"{serializer.validated_data['full_name']}\n"
            f"Phone: {serializer.validated_data['phone']}\n"
            f"{serializer.validated_data['street_address']}"
            f"{', ' + serializer.validated_data['apartment_suite'] if serializer.validated_data.get('apartment_suite') else ''}\n"
            f"{serializer.validated_data['city']}, {serializer.validated_data['state']} - {serializer.validated_data['postal_code']}\n"
            f"{'Landmark: ' + serializer.validated_data['landmark'] if serializer.validated_data.get('landmark') else ''}"
        )

        # Generate unique POCKET order number: PKT-YYYYMMDD-XXXX
        order_number = f"PKT-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # Link authenticated user or create guest customer account
        if request.user.is_authenticated:
            user = request.user
        else:
            phone = serializer.validated_data['phone']
            full_name = serializer.validated_data['full_name']
            username = f"guest_{phone}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'phone_number': phone,
                    'first_name': full_name.split()[0] if full_name else 'Guest',
                    'last_name': ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else 'Customer',
                }
            )

        with transaction.atomic():
            order = Order.objects.create(
                order_number=order_number,
                user=user,
                shipping_address_snapshot=address_snapshot,
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                total_amount=total_amount,
                status='PENDING_PAYMENT',
                payment_status='UNPAID',
                customer_notes=serializer.validated_data.get('customer_notes', '')
            )

            # Copy cart items into OrderItem records with price snapshots
            for item in cart.items.all():
                variant_desc = f"{item.variant.size} / {item.variant.color}" if item.variant else "Standard"
                unit_price = item.product.selling_price
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    product_name=item.product.name,
                    variant_details=variant_desc,
                    unit_price=unit_price,
                    quantity=item.quantity,
                    total_price=unit_price * item.quantity
                )

            # Record initial order status history
            OrderStatusHistory.objects.create(
                order=order,
                status='PENDING_PAYMENT',
                comment='Order created. Awaiting UPI payment reference submission.'
            )

            # Clear cart items
            cart.items.all().delete()

        order_data = OrderDetailSerializer(order).data
        return Response({
            "message": "Order created successfully. Please complete UPI payment.",
            "order": order_data,
            "payment_instructions": {
                "upi_id": config.upi_id,
                "account_display_name": config.account_display_name,
                "amount": str(total_amount),
                "order_number": order_number,
                "qr_intent_url": f"upi://pay?pa={config.upi_id}&pn={config.account_display_name}&am={total_amount}&cu=INR&tn=POCKET Order {order_number}"
            }
        }, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, order_number):
        qs = Order.objects.filter(order_number=order_number).prefetch_related('items', 'status_history')
        if request.user.is_authenticated and not request.user.is_staff:
            qs = qs.filter(user=request.user)
        order = qs.first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(OrderDetailSerializer(order).data)


class OrderTrackView(APIView):
    """Guest order tracking using order number and phone."""
    permission_classes = [AllowAny]

    def get(self, request):
        order_number = request.query_params.get('order_number', '').strip()
        phone = request.query_params.get('phone', '').strip()

        if not order_number or not phone:
            return Response({"detail": "Both order_number and phone are required."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.filter(order_number=order_number, shipping_address_snapshot__icontains=phone).first()
        if not order:
            return Response({"detail": "No matching order found for provided details."}, status=status.HTTP_404_NOT_FOUND)

        return Response(OrderDetailSerializer(order).data)


# ----------------------------------------------------
# 6. PAYMENTS API (UPI & UTR VERIFICATION)
# ----------------------------------------------------

class UPIDetailsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        order_number = request.query_params.get('order_number')
        if not order_number:
            return Response({"detail": "order_number is required."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.filter(order_number=order_number).first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        config = SiteConfiguration.get_solo()
        intent_url = f"upi://pay?pa={config.upi_id}&pn={config.account_display_name}&am={order.total_amount}&cu=INR&tn=POCKET Order {order.order_number}"

        data = {
            "order_number": order.order_number,
            "amount": order.total_amount,
            "upi_id": config.upi_id,
            "account_display_name": config.account_display_name,
            "upi_intent_url": intent_url,
            "payment_instructions": config.payment_instructions
        }
        return Response(UPIDetailsSerializer(data).data)


class SubmitUTRView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SubmitUTRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_number = serializer.validated_data['order_number']
        utr = serializer.validated_data['utr_number']
        payer_name = serializer.validated_data['payer_name']
        payer_phone = serializer.validated_data['payer_phone']

        order = Order.objects.filter(order_number=order_number).first()
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            # Create or update Payment record
            payment, _ = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'payment_method': 'UPI_QR',
                    'utr_number': utr,
                    'amount': order.total_amount,
                    'status': 'UNDER_VERIFICATION',
                    'payer_name': payer_name,
                }
            )
            payment.utr_number = utr
            payment.payer_name = payer_name
            payment.status = 'UNDER_VERIFICATION'
            payment.save()

            # Update Order Status (STRICT: DOES NOT CONFIRM - ONLY ENTERS VERIFICATION)
            order.status = 'PAYMENT_UNDER_VERIFICATION'
            order.save()

            OrderStatusHistory.objects.create(
                order=order,
                status='PAYMENT_UNDER_VERIFICATION',
                comment=f"Customer submitted UPI UTR: {utr}. Awaiting manual bank verification by POCKET admin."
            )

        return Response({
            "message": "Payment reference submitted successfully. Our team will verify the payment and confirm your order shortly.",
            "order_number": order.order_number,
            "utr_number": utr,
            "status": "PAYMENT_UNDER_VERIFICATION"
        }, status=status.HTTP_200_OK)


# ----------------------------------------------------
# 7. CUSTOMER AUTHENTICATION & PROFILE API
# ----------------------------------------------------

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Account created successfully.",
            "user": UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username_or_email = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')

        if not username_or_email or not password:
            return Response({"detail": "Please provide both username/email and password."}, status=status.HTTP_400_BAD_REQUEST)

        # Allow login via username or email
        user = None
        if '@' in username_or_email:
            u_obj = User.objects.filter(email__iexact=username_or_email).first()
            if u_obj:
                user = authenticate(request, username=u_obj.username, password=password)
        else:
            user = authenticate(request, username=username_or_email, password=password)

        if not user:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        cart, session_key = _resolve_cart(request)

        resp = Response({
            "message": "Logged in successfully.",
            "user": UserProfileSerializer(user).data,
            "cart": CartSerializer(cart, context={'request': request}).data
        })
        if session_key:
            resp['X-Session-Key'] = session_key
        return resp


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CustomerAddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = request.user.addresses.all()
        return Response(CustomerAddressSerializer(addresses, many=True).data)

    def post(self, request):
        serializer = CustomerAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

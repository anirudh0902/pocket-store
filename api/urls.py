from django.urls import path
from .views import (
    HealthCheckView,
    CategoryListView,
    CategoryDetailView,
    ProductListView,
    ProductDetailView,
    CartDetailView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    ClearCartView,
    CheckoutView,
    OrderDetailView,
    OrderTrackView,
    UPIDetailsView,
    SubmitUTRView,
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    CustomerAddressListCreateView,
)

app_name = 'api'

urlpatterns = [
    # System Health
    path('health/', HealthCheckView.as_view(), name='health_check'),

    # Category Catalog
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),

    # Product Catalog & Search
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),

    # Cart Management (Auth & Guest Session Token)
    path('cart/', CartDetailView.as_view(), name='cart_detail'),
    path('cart/add/', AddToCartView.as_view(), name='cart_add'),
    path('cart/update/<int:item_id>/', UpdateCartItemView.as_view(), name='cart_update'),
    path('cart/remove/<int:item_id>/', RemoveCartItemView.as_view(), name='cart_remove'),
    path('cart/clear/', ClearCartView.as_view(), name='cart_clear'),

    # Checkout & Orders
    path('orders/checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/track/', OrderTrackView.as_view(), name='order_track'),
    path('orders/<str:order_number>/', OrderDetailView.as_view(), name='order_detail'),

    # Payments & UPI UTR Verification
    path('payments/upi-details/', UPIDetailsView.as_view(), name='upi_details'),
    path('payments/submit-utr/', SubmitUTRView.as_view(), name='submit_utr'),

    # Customer Authentication & Profile
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/addresses/', CustomerAddressListCreateView.as_view(), name='address_list_create'),
]

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Built-in Django Admin (secondary)
    path('django-admin/', admin.site.urls),

    # Core & Storefront
    path('', include('core.urls')),

    # Customer Authentication & Accounts
    path('accounts/', include('accounts.urls')),

    # Product Catalog & Categories
    path('shop/', include('products.urls')),

    # Orders, Cart & Wishlist
    path('orders/', include('orders.urls')),

    # Payments & UPI Verification
    path('payments/', include('payments.urls')),

    # Custom POCKET Admin Dashboard & Management
    path('admin-portal/', include('admin_dashboard.urls')),

    # In-App Notifications
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

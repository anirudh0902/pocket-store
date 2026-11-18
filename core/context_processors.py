from django.conf import settings
from products.models import Category
from payments.models import SiteConfiguration
from orders.models import Cart, Wishlist
from notifications.models import Notification


def site_context(request):
    """
    Site-wide context processor providing brand information, navigation categories,
    cart badge count, wishlist badge count, and unread notifications badge count.
    """
    try:
        config = SiteConfiguration.get_solo()
    except Exception:
        config = None

    try:
        nav_categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')[:8]
    except Exception:
        nav_categories = []

    cart_count = 0
    wishlist_count = 0
    unread_notifications_count = 0

    if request.user.is_authenticated:
        # Wishlist count
        try:
            wishlist = getattr(request.user, 'wishlist', None)
            if wishlist:
                wishlist_count = wishlist.items.count()
        except Exception:
            wishlist_count = 0

        # Notifications count
        try:
            unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        except Exception:
            unread_notifications_count = 0

        # Cart count
        try:
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                cart_count = cart.total_items_count
        except Exception:
            cart_count = 0
    else:
        # Guest cart count
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.filter(session_key=session_key).first()
                if cart:
                    cart_count = cart.total_items_count
            except Exception:
                cart_count = 0

    return {
        'brand': settings.POCKET_BRAND,
        'site_config': config,
        'nav_categories': nav_categories,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'unread_notifications_count': unread_notifications_count,
    }

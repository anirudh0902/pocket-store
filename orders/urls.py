from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Cart
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add_view, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update_view, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove_view, name='cart_remove'),

    # Wishlist
    path('wishlist/', views.wishlist_detail_view, name='wishlist_detail'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle_view, name='wishlist_toggle'),
    path('wishlist/move-to-cart/<int:item_id>/', views.wishlist_move_to_cart_view, name='wishlist_move_to_cart'),

    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),
]

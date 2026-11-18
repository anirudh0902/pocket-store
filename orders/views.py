from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product, ProductVariant
from accounts.models import CustomerAddress
from notifications.models import Notification
from .models import Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem, OrderStatusHistory


def get_or_create_cart(request):
    """Helper to safely retrieve or initialize active shopping cart."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_detail_view(request):
    """
    Shopping cart page.
    Recalculates all pricing and verifies stock availability dynamically on server.
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'variant').all()

    return render(request, 'orders/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items,
    })


@require_POST
def cart_add_view(request, product_id):
    """
    Adds a product with selected variant (size/color) and quantity to cart.
    Always validated on server.
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_or_create_cart(request)

    # Variant selection (size/color)
    variant_id = request.POST.get('variant_id')
    size = request.POST.get('size', '').strip()
    color = request.POST.get('color', '').strip()
    
    variant = None
    if variant_id:
        variant = ProductVariant.objects.filter(pk=variant_id, product=product, is_active=True).first()
    elif size or color:
        q = product.variants.filter(is_active=True)
        if size:
            q = q.filter(size=size)
        if color:
            q = q.filter(color=color)
        variant = q.first()

    # Quantity validation
    try:
        qty = int(request.POST.get('quantity', 1))
        if qty < 1:
            qty = 1
        elif qty > 10:
            qty = 10
    except (ValueError, TypeError):
        qty = 1

    # Check inventory
    max_stock = variant.stock_quantity if variant else product.stock_quantity
    if max_stock > 0 and qty > max_stock:
        qty = max_stock
        messages.warning(request, f"Quantity adjusted to maximum available stock ({max_stock}).")

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': qty}
    )
    if not created:
        cart_item.quantity += qty
        if max_stock > 0 and cart_item.quantity > max_stock:
            cart_item.quantity = max_stock
        cart_item.save()

    messages.success(request, f"Added '{product.name}' to your shopping cart.")

    # Check if 'buy_now' was clicked
    if request.POST.get('buy_now') == '1':
        return redirect('orders:checkout')

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'orders:cart_detail')


@require_POST
def cart_update_view(request, item_id):
    """Updates item quantity in cart with stock bounds check."""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    try:
        new_qty = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        new_qty = 1

    if new_qty <= 0:
        cart_item.delete()
        messages.info(request, f"Removed '{cart_item.product.name}' from your cart.")
    else:
        max_stock = cart_item.variant.stock_quantity if cart_item.variant else cart_item.product.stock_quantity
        if max_stock > 0 and new_qty > max_stock:
            new_qty = max_stock
            messages.warning(request, f"Only {max_stock} units available in stock.")
        cart_item.quantity = new_qty
        cart_item.save()
        messages.success(request, "Cart quantity updated.")

    return redirect('orders:cart_detail')


@require_POST
def cart_remove_view(request, item_id):
    """Removes single item from cart."""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.info(request, f"Removed '{product_name}' from your cart.")
    return redirect('orders:cart_detail')


@login_required
def wishlist_detail_view(request):
    """Customer wishlist."""
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product').all()
    return render(request, 'orders/wishlist.html', {'wishlist': wishlist, 'items': items})


@login_required
@require_POST
def wishlist_toggle_view(request, product_id):
    """Adds or removes product from customer's wishlist."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    existing = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
    if existing:
        existing.delete()
        messages.info(request, f"Removed '{product.name}' from your wishlist.")
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        messages.success(request, f"Saved '{product.name}' to your wishlist.")

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'orders:wishlist_detail')


@login_required
@require_POST
def wishlist_move_to_cart_view(request, item_id):
    """Moves an item from wishlist to active cart."""
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist_item = get_object_or_404(WishlistItem, pk=item_id, wishlist=wishlist)
    product = wishlist_item.product

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=None,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    wishlist_item.delete()
    messages.success(request, f"Moved '{product.name}' to your shopping cart.")
    return redirect('orders:cart_detail')


@login_required
def checkout_view(request):
    """
    Checkout & Order Creation.
    Validates delivery address and cart contents.
    COD is strictly prohibited: explicitly states online payment is required.
    Creates Order record with financial snapshots and redirects to UPI payment.
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'variant').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Please add items to checkout.")
        return redirect('products:product_list')

    user_addresses = request.user.addresses.all()

    if request.method == 'POST':
        # Check whether user chose existing address or submitted a new address
        address_id = request.POST.get('address_id')
        address = None
        
        if address_id:
            address = get_object_or_404(CustomerAddress, pk=address_id, user=request.user)
            address_snapshot = address.to_snapshot()
        else:
            # New address submitted directly on checkout
            full_name = request.POST.get('full_name', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            alternate_phone = request.POST.get('alternate_phone', '').strip()
            address_line_1 = request.POST.get('address_line_1', '').strip()
            address_line_2 = request.POST.get('address_line_2', '').strip()
            landmark = request.POST.get('landmark', '').strip()
            city = request.POST.get('city', '').strip()
            state = request.POST.get('state', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            save_address = request.POST.get('save_address') == 'on'

            if not full_name or not phone_number or not address_line_1 or not city or not state or not pincode:
                messages.error(request, "Please provide complete delivery address details.")
                return render(request, 'orders/checkout.html', {
                    'cart': cart,
                    'cart_items': cart_items,
                    'user_addresses': user_addresses,
                })

            address_snapshot = {
                'full_name': full_name,
                'phone_number': phone_number,
                'alternate_phone': alternate_phone,
                'address_line_1': address_line_1,
                'address_line_2': address_line_2,
                'landmark': landmark,
                'city': city,
                'state': state,
                'pincode': pincode,
                'address_type': 'HOME',
            }

            if save_address:
                CustomerAddress.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone_number=phone_number,
                    alternate_phone=alternate_phone,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    landmark=landmark,
                    city=city,
                    state=state,
                    pincode=pincode,
                    is_default=(not user_addresses.exists())
                )

        customer_notes = request.POST.get('customer_notes', '').strip()

        # Recalculate totals on server
        subtotal = cart.subtotal
        shipping_fee = cart.shipping_charge
        total_amount = cart.grand_total

        # Compute internal supplier cost snapshot
        total_supplier_cost = Decimal('0.00')
        for item in cart_items:
            unit_cost = item.product.source_cost
            total_supplier_cost += (unit_cost * item.quantity)

        # Create Order
        order = Order.objects.create(
            user=request.user,
            shipping_address_snapshot=address_snapshot,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            status='PENDING_PAYMENT',
            payment_status='UNPAID',
            total_supplier_cost=total_supplier_cost,
            customer_notes=customer_notes,
        )

        # Create OrderItems with frozen price and supplier cost snapshots
        for item in cart_items:
            unit_price = item.unit_price
            variant_desc = ""
            if item.variant:
                parts = []
                if item.variant.size: parts.append(f"Size: {item.variant.size}")
                if item.variant.color: parts.append(f"Color: {item.variant.color}")
                variant_desc = ", ".join(parts)

            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                product_name=item.product.name,
                variant_details=variant_desc,
                unit_price=unit_price,
                supplier_unit_cost=item.product.source_cost,
                quantity=item.quantity,
                total_price=(unit_price * item.quantity),
            )

        # Record Initial Status History
        OrderStatusHistory.objects.create(
            order=order,
            status='PENDING_PAYMENT',
            comment="Order placed by customer. Awaiting UPI payment submission.",
            customer_visible=True
        )

        # Create in-app Notification
        Notification.objects.create(
            user=request.user,
            order=order,
            title="Order Placed Successfully",
            message=f"Your order #{order.order_number} for ₹{order.total_amount} has been placed. Please complete UPI payment to confirm.",
            notification_type='ORDER_PLACED'
        )

        # Clear active cart
        cart_items.delete()

        # Redirect to UPI payment page
        messages.success(request, f"Order #{order.order_number} created! Please complete UPI payment below.")
        return redirect('payments:upi_payment', order_number=order.order_number)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'user_addresses': user_addresses,
    })

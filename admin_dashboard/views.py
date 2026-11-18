import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg, F
from django.utils import timezone
from django.core.paginator import Paginator

from accounts.models import User
from products.models import Product, Category, ProductImage, ProductVariant
from orders.models import Order, OrderItem, OrderStatusHistory, ShippingDetails
from payments.models import Payment, SiteConfiguration
from notifications.models import Notification
from .models import Supplier, BusinessExpense


def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.is_pocket_admin)


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def dashboard_overview_view(request):
    """
    Main business dashboard overview.
    All metrics computed from live database records.
    """
    # Core Counts
    total_orders = Order.objects.count()
    total_customers = User.objects.filter(is_customer=True).count()
    total_products = Product.objects.count()

    # Order Pipeline Counts
    pending_payments = Order.objects.filter(status='PENDING_PAYMENT').count()
    verification_payments = Order.objects.filter(status='PAYMENT_VERIFICATION').count()
    verified_payments = Order.objects.filter(payment_status='VERIFIED').count()
    processing_orders = Order.objects.filter(status__in=['PAYMENT_VERIFIED', 'PROCESSING', 'SUPPLIER_ORDER_PLACED']).count()
    shipped_orders = Order.objects.filter(status__in=['SHIPPED', 'OUT_FOR_DELIVERY']).count()
    delivered_orders = Order.objects.filter(status='DELIVERED').count()
    cancelled_orders = Order.objects.filter(status='CANCELLED').count()

    # Financials (Only verified & non-cancelled orders count towards realized revenue)
    active_orders = Order.objects.filter(payment_status='VERIFIED').exclude(status='CANCELLED')
    total_revenue = active_orders.aggregate(s=Sum('total_amount'))['s'] or Decimal('0.00')
    total_profit = active_orders.aggregate(s=Sum('estimated_profit'))['s'] or Decimal('0.00')
    total_supplier_costs = active_orders.aggregate(s=Sum('total_supplier_cost'))['s'] or Decimal('0.00')

    # Recent items
    recent_orders = Order.objects.order_by('-created_at')[:6]
    pending_payments_list = Payment.objects.filter(status='PENDING').select_related('order', 'order__user')[:5]

    return render(request, 'admin_dashboard/overview.html', {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'pending_payments': pending_payments,
        'verification_payments': verification_payments,
        'verified_payments': verified_payments,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'total_supplier_costs': total_supplier_costs,
        'recent_orders': recent_orders,
        'pending_payments_list': pending_payments_list,
    })


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_product_list_view(request):
    """Lists products with stock warnings, filtering, and quick actions."""
    products = Product.objects.select_related('category', 'supplier').prefetch_related('images').all()

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(supplier_sku_or_url__icontains=query)
        )

    cat_id = request.GET.get('category')
    if cat_id:
        products = products.filter(category_id=cat_id)

    status_filter = request.GET.get('status')
    if status_filter == 'active':
        products = products.filter(is_active=True)
    elif status_filter == 'inactive':
        products = products.filter(is_active=False)
    elif status_filter == 'low_stock':
        products = products.filter(stock_quantity__lte=5)

    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()

    return render(request, 'admin_dashboard/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'cat_id': cat_id,
        'status_filter': status_filter,
    })


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_product_create_view(request):
    """Adds a new product including images, variants, and private supplier costs."""
    categories = Category.objects.all()
    suppliers = Supplier.objects.filter(is_active=True)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        description = request.POST.get('description', '').strip()
        specifications = request.POST.get('specifications', '').strip()
        selling_price = request.POST.get('selling_price')
        original_price = request.POST.get('original_price') or None
        source_cost = request.POST.get('source_cost') or 0.00
        supplier_id = request.POST.get('supplier') or None
        supplier_sku_or_url = request.POST.get('supplier_sku_or_url', '').strip()
        stock_quantity = request.POST.get('stock_quantity', 0)
        is_active = request.POST.get('is_active') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        is_bestseller = request.POST.get('is_bestseller') == 'on'
        is_trending = request.POST.get('is_trending') == 'on'
        delivery_info = request.POST.get('delivery_info', '').strip()
        return_policy_info = request.POST.get('return_policy_info', '').strip()

        if not name or not selling_price:
            messages.error(request, "Product name and selling price are required.")
            return render(request, 'admin_dashboard/product_form.html', {
                'categories': categories, 'suppliers': suppliers, 'title': 'Add New Product'
            })

        category = Category.objects.filter(pk=category_id).first() if category_id else None
        supplier = Supplier.objects.filter(pk=supplier_id).first() if supplier_id else None

        product = Product.objects.create(
            name=name,
            category=category,
            description=description,
            specifications=specifications,
            selling_price=Decimal(selling_price),
            original_price=Decimal(original_price) if original_price else None,
            source_cost=Decimal(source_cost),
            supplier=supplier,
            supplier_sku_or_url=supplier_sku_or_url,
            stock_quantity=int(stock_quantity),
            is_active=is_active,
            is_featured=is_featured,
            is_bestseller=is_bestseller,
            is_trending=is_trending,
            delivery_info=delivery_info or "Free delivery on orders above ₹499. Dispatched in 24-48 hours.",
            return_policy_info=return_policy_info or "7-day replacement or return in case of damaged/defective item.",
        )

        # Handle Multiple Image Uploads
        images = request.FILES.getlist('images')
        for idx, img in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=img,
                is_primary=(idx == 0),
                display_order=idx
            )

        # Handle Variants (Sizes/Colors)
        sizes_input = request.POST.get('variants_sizes', '').strip()
        colors_input = request.POST.get('variants_colors', '').strip()
        if sizes_input:
            for s in [x.strip() for x in sizes_input.split(',') if x.strip()]:
                ProductVariant.objects.create(
                    product=product,
                    size=s,
                    stock_quantity=int(stock_quantity) // (len(sizes_input.split(',')) or 1)
                )

        messages.success(request, f"Product '{product.name}' created successfully.")
        return redirect('admin_dashboard:product_list')

    return render(request, 'admin_dashboard/product_form.html', {
        'categories': categories,
        'suppliers': suppliers,
        'title': 'Add New Product'
    })


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_product_edit_view(request, pk):
    """Edits an existing product."""
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    suppliers = Supplier.objects.filter(is_active=True)

    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        product.category = Category.objects.filter(pk=category_id).first() if category_id else None
        product.description = request.POST.get('description', '').strip()
        product.specifications = request.POST.get('specifications', '').strip()
        product.selling_price = Decimal(request.POST.get('selling_price', '0.00'))
        
        orig_price = request.POST.get('original_price')
        product.original_price = Decimal(orig_price) if orig_price else None
        
        product.source_cost = Decimal(request.POST.get('source_cost', '0.00'))
        supplier_id = request.POST.get('supplier')
        product.supplier = Supplier.objects.filter(pk=supplier_id).first() if supplier_id else None
        product.supplier_sku_or_url = request.POST.get('supplier_sku_or_url', '').strip()
        
        product.stock_quantity = int(request.POST.get('stock_quantity', 0))
        product.is_active = request.POST.get('is_active') == 'on'
        product.is_featured = request.POST.get('is_featured') == 'on'
        product.is_bestseller = request.POST.get('is_bestseller') == 'on'
        product.is_trending = request.POST.get('is_trending') == 'on'
        product.delivery_info = request.POST.get('delivery_info', '').strip()
        product.return_policy_info = request.POST.get('return_policy_info', '').strip()
        product.save()

        # Handle Additional Image Uploads
        new_images = request.FILES.getlist('images')
        for img in new_images:
            ProductImage.objects.create(
                product=product,
                image=img,
                is_primary=(not product.images.exists()),
                display_order=product.images.count()
            )

        messages.success(request, f"Product '{product.name}' updated successfully.")
        return redirect('admin_dashboard:product_list')

    return render(request, 'admin_dashboard/product_form.html', {
        'product': product,
        'categories': categories,
        'suppliers': suppliers,
        'title': f'Edit Product: {product.name}'
    })


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
@require_POST
def admin_product_toggle_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save()
    status_text = "activated" if product.is_active else "deactivated"
    messages.success(request, f"Product '{product.name}' has been {status_text}.")
    return redirect('admin_dashboard:product_list')


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' was deleted.")
        return redirect('admin_dashboard:product_list')
    return render(request, 'admin_dashboard/confirm_delete.html', {
        'item': product,
        'item_type': 'Product',
        'cancel_url': 'admin_dashboard:product_list'
    })


# CATEGORY MANAGEMENT
@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_category_list_view(request):
    categories = Category.objects.all().order_by('display_order', 'name')
    return render(request, 'admin_dashboard/category_list.html', {'categories': categories})


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_category_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        display_order = request.POST.get('display_order', 0)
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')

        if not name:
            messages.error(request, "Category name is required.")
            return render(request, 'admin_dashboard/category_form.html')

        Category.objects.create(
            name=name,
            description=description,
            display_order=int(display_order or 0),
            is_active=is_active,
            image=image
        )
        messages.success(request, f"Category '{name}' created successfully.")
        return redirect('admin_dashboard:category_list')

    return render(request, 'admin_dashboard/category_form.html', {'title': 'Add New Category'})


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_category_edit_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        category.description = request.POST.get('description', '').strip()
        category.display_order = int(request.POST.get('display_order', 0) or 0)
        category.is_active = request.POST.get('is_active') == 'on'
        if request.FILES.get('image'):
            category.image = request.FILES.get('image')
        category.save()
        messages.success(request, f"Category '{category.name}' updated successfully.")
        return redirect('admin_dashboard:category_list')
    return render(request, 'admin_dashboard/category_form.html', {'category': category, 'title': f'Edit Category: {category.name}'})


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' deleted.")
        return redirect('admin_dashboard:category_list')
    return render(request, 'admin_dashboard/confirm_delete.html', {
        'item': category,
        'item_type': 'Category',
        'cancel_url': 'admin_dashboard:category_list'
    })


# SUPPLIER MANAGEMENT (INTERNAL)
@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_supplier_list_view(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'admin_dashboard/supplier_list.html', {'suppliers': suppliers})


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_supplier_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        platform = request.POST.get('platform', 'MEESHO')
        contact_person = request.POST.get('contact_person', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        website_or_store_url = request.POST.get('website_or_store_url', '').strip()
        internal_notes = request.POST.get('internal_notes', '').strip()

        if not name:
            messages.error(request, "Supplier name is required.")
            return render(request, 'admin_dashboard/supplier_form.html')

        Supplier.objects.create(
            name=name,
            platform=platform,
            contact_person=contact_person,
            phone=phone,
            email=email,
            website_or_store_url=website_or_store_url,
            internal_notes=internal_notes
        )
        messages.success(request, f"Supplier '{name}' registered.")
        return redirect('admin_dashboard:supplier_list')

    return render(request, 'admin_dashboard/supplier_form.html', {'title': 'Add Supplier Record'})


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_supplier_edit_view(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.name = request.POST.get('name', '').strip()
        supplier.platform = request.POST.get('platform', 'MEESHO')
        supplier.contact_person = request.POST.get('contact_person', '').strip()
        supplier.phone = request.POST.get('phone', '').strip()
        supplier.email = request.POST.get('email', '').strip()
        supplier.website_or_store_url = request.POST.get('website_or_store_url', '').strip()
        supplier.internal_notes = request.POST.get('internal_notes', '').strip()
        supplier.is_active = request.POST.get('is_active') == 'on'
        supplier.save()
        messages.success(request, f"Supplier '{supplier.name}' updated.")
        return redirect('admin_dashboard:supplier_list')
    return render(request, 'admin_dashboard/supplier_form.html', {'supplier': supplier, 'title': f'Edit Supplier: {supplier.name}'})


# ORDER MANAGEMENT & FULFILLMENT
@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_order_list_view(request):
    orders = Order.objects.select_related('user', 'supplier').prefetch_related('items', 'payments').order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    payment_status_filter = request.GET.get('payment_status')
    if payment_status_filter:
        orders = orders.filter(payment_status=payment_status_filter)

    query = request.GET.get('q', '').strip()
    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(shipping_address_snapshot__full_name__icontains=query) |
            Q(shipping_address_snapshot__phone_number__icontains=query)
        )

    paginator = Paginator(orders, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_dashboard/order_list.html', {
        'page_obj': page_obj,
        'status_choices': Order.STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
        'status_filter': status_filter,
        'payment_status_filter': payment_status_filter,
        'query': query,
    })


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    order_items = order.items.select_related('product', 'variant').all()
    status_history = order.status_history.order_by('-created_at')
    payments = order.payments.order_by('-created_at')
    suppliers = Supplier.objects.filter(is_active=True)

    return render(request, 'admin_dashboard/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'status_history': status_history,
        'payments': payments,
        'suppliers': suppliers,
        'status_choices': Order.STATUS_CHOICES,
    })


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
@require_POST
def admin_order_update_status_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    new_status = request.POST.get('status')
    comment = request.POST.get('comment', '').strip()

    valid_statuses = dict(Order.STATUS_CHOICES).keys()
    if new_status in valid_statuses:
        old_status_display = order.get_status_display()
        order.status = new_status
        order.save()

        # Create history entry
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            changed_by=request.user,
            comment=comment or f"Status updated from {old_status_display} to {order.get_status_display()}.",
            customer_visible=True
        )

        # Notify customer
        Notification.objects.create(
            user=order.user,
            order=order,
            title=f"Order Status Update: {order.get_status_display()}",
            message=comment or f"Your order #{order.order_number} is now {order.get_status_display()}.",
            notification_type='PROCESSING'
        )

        messages.success(request, f"Order status updated to {order.get_status_display()}.")
    else:
        messages.error(request, "Invalid status transition.")

    return redirect('admin_dashboard:order_detail', order_number=order.order_number)


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
@require_POST
def admin_order_supplier_fulfillment_view(request, order_number):
    """
    Records internal supplier purchase details.
    CRITICAL: Does not allow placing supplier order before payment verification!
    """
    order = get_object_or_404(Order, order_number=order_number)

    if order.payment_status != 'VERIFIED':
        messages.error(request, "Cannot place supplier order before payment is verified! Please verify customer payment first.")
        return redirect('admin_dashboard:order_detail', order_number=order.order_number)

    supplier_id = request.POST.get('supplier_id')
    supplier_ref = request.POST.get('supplier_order_reference', '').strip()
    internal_notes = request.POST.get('internal_notes', '').strip()

    if supplier_id:
        order.supplier = Supplier.objects.filter(pk=supplier_id).first()
    order.supplier_order_reference = supplier_ref
    order.supplier_order_date = timezone.now()
    if internal_notes:
        order.internal_notes = internal_notes
    
    order.status = 'SUPPLIER_ORDER_PLACED'
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status='SUPPLIER_ORDER_PLACED',
        changed_by=request.user,
        comment="Order is being processed with our fulfillment partner.",
        customer_visible=True
    )

    Notification.objects.create(
        user=order.user,
        order=order,
        title="Order Processing with Fulfillment Partner",
        message=f"Order #{order.order_number} has been forwarded for packaging and dispatch.",
        notification_type='SUPPLIER_ORDER_PLACED'
    )

    messages.success(request, "Supplier order placement recorded successfully.")
    return redirect('admin_dashboard:order_detail', order_number=order.order_number)


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
@require_POST
def admin_order_shipping_dispatch_view(request, order_number):
    """
    Adds courier dispatch tracking details (courier partner, AWB, URL).
    Transitions status to SHIPPED and notifies customer with tracking info.
    """
    order = get_object_or_404(Order, order_number=order_number)
    courier = request.POST.get('courier_partner', '').strip()
    tracking_num = request.POST.get('tracking_number', '').strip()
    tracking_url = request.POST.get('tracking_url', '').strip()
    notes = request.POST.get('notes', '').strip()

    if not courier or not tracking_num:
        messages.error(request, "Courier partner and tracking number are required.")
        return redirect('admin_dashboard:order_detail', order_number=order.order_number)

    shipping_details, created = ShippingDetails.objects.get_or_create(order=order, defaults={
        'courier_partner': courier,
        'tracking_number': tracking_num,
        'tracking_url': tracking_url,
        'dispatched_date': timezone.now(),
        'notes': notes,
    })
    if not created:
        shipping_details.courier_partner = courier
        shipping_details.tracking_number = tracking_num
        shipping_details.tracking_url = tracking_url
        shipping_details.dispatched_date = timezone.now()
        shipping_details.notes = notes
        shipping_details.save()

    order.status = 'SHIPPED'
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status='SHIPPED',
        changed_by=request.user,
        comment=f"Dispatched via {courier} (Tracking: {tracking_num}).",
        customer_visible=True
    )

    Notification.objects.create(
        user=order.user,
        order=order,
        title="Your Order has been Shipped!",
        message=f"Order #{order.order_number} has been dispatched via {courier}. Tracking Number: {tracking_num}.",
        notification_type='SHIPPED'
    )

    messages.success(request, f"Shipping tracking details saved. Order marked as SHIPPED.")
    return redirect('admin_dashboard:order_detail', order_number=order.order_number)


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
@require_POST
def admin_order_expenses_update_view(request, order_number):
    """
    Updates internal operational expenses for the order to keep net profit exact.
    """
    order = get_object_or_404(Order, order_number=order_number)

    actual_shipping = request.POST.get('actual_shipping_expense', 0)
    packaging = request.POST.get('packaging_expense', 0)
    payment_charges = request.POST.get('payment_gateway_charges', 0)
    other_exp = request.POST.get('other_expenses', 0)

    try:
        order.actual_shipping_expense = Decimal(str(actual_shipping or 0))
        order.packaging_expense = Decimal(str(packaging or 0))
        order.payment_gateway_charges = Decimal(str(payment_charges or 0))
        order.other_expenses = Decimal(str(other_exp or 0))
        order.calculate_profit()
        order.save()
        messages.success(request, f"Order expenses updated. Estimated profit: ₹{order.estimated_profit}.")
    except Exception as e:
        messages.error(request, f"Error updating expenses: {str(e)}")

    return redirect('admin_dashboard:order_detail', order_number=order.order_number)


# PAYMENT VERIFICATION
@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_payment_list_view(request):
    """Shows all submitted payments with quick approve/reject buttons."""
    payments = Payment.objects.select_related('order', 'order__user', 'verified_by').order_by('-created_at')
    
    status_filter = request.GET.get('status', 'PENDING')
    if status_filter != 'ALL':
        payments = payments.filter(status=status_filter)

    query = request.GET.get('q', '').strip()
    if query:
        payments = payments.filter(
            Q(utr_number__icontains=query) |
            Q(order__order_number__icontains=query) |
            Q(payer_name__icontains=query) |
            Q(payer_upi_id__icontains=query)
        )

    paginator = Paginator(payments, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_dashboard/payment_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'query': query,
    })


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
@require_POST
def admin_payment_approve_view(request, pk):
    """
    Authorized admin approves payment after verifying bank account receipt.
    """
    payment = get_object_or_404(Payment, pk=pk)
    admin_notes = request.POST.get('admin_notes', '').strip()
    payment.approve(admin_user=request.user, notes=admin_notes)

    Notification.objects.create(
        user=payment.order.user,
        order=payment.order,
        title="Payment Verified & Confirmed!",
        message=f"Your payment of ₹{payment.amount} for Order #{payment.order.order_number} has been verified and approved. Your order is now confirmed!",
        notification_type='PAYMENT_VERIFIED'
    )

    messages.success(request, f"Payment for Order #{payment.order.order_number} has been APPROVED and marked as Paid.")
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'admin_dashboard:payment_list')


@user_passes_test(is_admin_or_staff, login_url='accounts:login')
@require_POST
def admin_payment_reject_view(request, pk):
    """
    Authorized admin rejects payment if UTR does not reflect in bank statement.
    """
    payment = get_object_or_404(Payment, pk=pk)
    reason = request.POST.get('reason', '').strip()
    payment.reject(admin_user=request.user, notes=reason)

    Notification.objects.create(
        user=payment.order.user,
        order=payment.order,
        title="Payment Verification Failed",
        message=f"UTR #{payment.utr_number} could not be verified in our bank statement. Reason: {reason or 'Transaction not found'}. Please re-submit or contact customer support.",
        notification_type='PAYMENT_REJECTED'
    )

    messages.warning(request, f"Payment for Order #{payment.order.order_number} was REJECTED.")
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'admin_dashboard:payment_list')


# FINANCIAL & PROFIT REPORTS
@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_financial_reports_view(request):
    """
    Comprehensive business analytics and net profit report.
    Formula: Estimated Profit = Selling Price - Supplier Cost - Shipping - Packaging - Payment Charges - Other Expenses.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - datetime.timedelta(days=7)
    month_start = today_start - datetime.timedelta(days=30)

    # All verified orders
    verified_orders = Order.objects.filter(payment_status='VERIFIED').exclude(status='CANCELLED')

    # Totals
    total_rev = verified_orders.aggregate(s=Sum('total_amount'))['s'] or Decimal('0.00')
    total_supplier = verified_orders.aggregate(s=Sum('total_supplier_cost'))['s'] or Decimal('0.00')
    total_shipping_exp = verified_orders.aggregate(s=Sum('actual_shipping_expense'))['s'] or Decimal('0.00')
    total_packaging = verified_orders.aggregate(s=Sum('packaging_expense'))['s'] or Decimal('0.00')
    total_payment_charges = verified_orders.aggregate(s=Sum('payment_gateway_charges'))['s'] or Decimal('0.00')
    total_other_expenses = verified_orders.aggregate(s=Sum('other_expenses'))['s'] or Decimal('0.00')
    total_profit = verified_orders.aggregate(s=Sum('estimated_profit'))['s'] or Decimal('0.00')

    # Time Breakdown
    daily_sales = verified_orders.filter(created_at__gte=today_start).aggregate(rev=Sum('total_amount'), prof=Sum('estimated_profit'), count=Count('id'))
    weekly_sales = verified_orders.filter(created_at__gte=week_start).aggregate(rev=Sum('total_amount'), prof=Sum('estimated_profit'), count=Count('id'))
    monthly_sales = verified_orders.filter(created_at__gte=month_start).aggregate(rev=Sum('total_amount'), prof=Sum('estimated_profit'), count=Count('id'))

    # Best-selling products
    bestselling_products = OrderItem.objects.filter(order__payment_status='VERIFIED').values('product__name').annotate(
        total_units=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_units')[:10]

    # Order Cancellation Rate
    all_orders_count = Order.objects.count()
    cancelled_orders_count = Order.objects.filter(status='CANCELLED').count()
    cancellation_rate = 0.0
    if all_orders_count > 0:
        cancellation_rate = round((cancelled_orders_count / all_orders_count) * 100, 1)

    return render(request, 'admin_dashboard/reports.html', {
        'total_revenue': total_rev,
        'total_supplier_cost': total_supplier,
        'total_shipping_expense': total_shipping_exp,
        'total_packaging': total_packaging,
        'total_payment_charges': total_payment_charges,
        'total_other_expenses': total_other_expenses,
        'total_profit': total_profit,
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'bestselling_products': bestselling_products,
        'all_orders_count': all_orders_count,
        'cancelled_orders_count': cancelled_orders_count,
        'cancellation_rate': cancellation_rate,
    })


# SETTINGS & UPI CONFIGURATION
@user_passes_test(is_admin_or_staff, login_url='accounts:login')
def admin_settings_view(request):
    config = SiteConfiguration.get_solo()

    if request.method == 'POST':
        config.site_name = request.POST.get('site_name', 'POCKET').strip()
        config.tagline = request.POST.get('tagline', 'Fashion that fits your pocket.').strip()
        config.upi_id = request.POST.get('upi_id', '').strip()
        config.account_display_name = request.POST.get('account_display_name', '').strip()
        config.payment_instructions = request.POST.get('payment_instructions', '').strip()
        
        free_thresh = request.POST.get('free_shipping_threshold')
        if free_thresh:
            config.free_shipping_threshold = Decimal(free_thresh)
            
        std_ship = request.POST.get('standard_shipping_charge')
        if std_ship:
            config.standard_shipping_charge = Decimal(std_ship)

        config.support_phone = request.POST.get('support_phone', '').strip()
        config.support_email = request.POST.get('support_email', '').strip()
        config.support_hours = request.POST.get('support_hours', '').strip()
        config.address = request.POST.get('address', '').strip()

        if request.FILES.get('qr_code_image'):
            config.qr_code_image = request.FILES.get('qr_code_image')

        config.save()
        messages.success(request, "Store and UPI Payment Configuration updated successfully.")
        return redirect('admin_dashboard:settings')

    return render(request, 'admin_dashboard/settings.html', {'config': config})

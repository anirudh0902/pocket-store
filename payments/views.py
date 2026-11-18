import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponseForbidden
from orders.models import Order, OrderStatusHistory
from notifications.models import Notification
from .models import SiteConfiguration, Payment


@login_required
def upi_payment_view(request, order_number):
    """
    Displays the configured UPI QR code, UPI ID, order details,
    and the form to submit transaction UTR number.
    Strictly restricted to the customer who placed the order or staff.
    """
    order = get_object_or_404(Order, order_number=order_number)

    if order.user != request.user and not (request.user.is_staff or request.user.is_pocket_admin):
        return HttpResponseForbidden("You are not authorized to view this payment page.")

    # If already verified, redirect directly to order details
    if order.payment_status == 'VERIFIED':
        messages.info(request, f"Order #{order.order_number} payment is already verified.")
        return redirect('accounts:order_detail', order_number=order.order_number)

    config = SiteConfiguration.get_solo()

    # Build UPI Deep-link URI
    # upi://pay?pa=...&pn=...&am=...&tn=...&cu=INR
    upi_params = {
        'pa': config.upi_id,
        'pn': config.account_display_name,
        'am': str(order.total_amount),
        'tn': f"POCKET-{order.order_number}",
        'cu': 'INR'
    }
    upi_uri = f"upi://pay?{urllib.parse.urlencode(upi_params)}"

    latest_payment = order.latest_payment

    return render(request, 'payments/upi_payment.html', {
        'order': order,
        'config': config,
        'upi_uri': upi_uri,
        'latest_payment': latest_payment,
    })


@login_required
@require_POST
def submit_payment_view(request, order_number):
    """
    Customer submits the 12-digit UPI UTR / Bank Reference number.
    CRITICAL SECURITY & INTEGRITY:
    - Does NOT automatically mark order as paid.
    - Sets order status to PAYMENT_VERIFICATION.
    - Prevents reuse of previously verified UTR numbers.
    - Stores submission for manual admin audit.
    """
    order = get_object_or_404(Order, order_number=order_number)

    if order.user != request.user and not (request.user.is_staff or request.user.is_pocket_admin):
        return HttpResponseForbidden("You are not authorized to submit payment for this order.")

    utr_number = request.POST.get('utr_number', '').strip().upper()
    payer_upi_id = request.POST.get('payer_upi_id', '').strip()
    payer_name = request.POST.get('payer_name', '').strip()
    screenshot = request.FILES.get('payment_screenshot')

    if not utr_number:
        messages.error(request, "Please enter the 12-digit UTR / Bank Reference number.")
        return redirect('payments:upi_payment', order_number=order.order_number)

    # Basic UTR sanity validation (alphanumeric, at least 6 characters, typically 12)
    if len(utr_number) < 6:
        messages.error(request, "Please enter a valid Bank Reference / UTR Number.")
        return redirect('payments:upi_payment', order_number=order.order_number)

    # Duplicate check: check if this UTR has already been verified for another order
    duplicate_verified = Payment.objects.filter(utr_number=utr_number, status='VERIFIED').exclude(order=order).exists()
    if duplicate_verified:
        messages.error(request, "This UTR / Reference number has already been used for another verified transaction. Please check your transaction details or contact support.")
        return redirect('payments:upi_payment', order_number=order.order_number)

    # Create Payment record with PENDING status
    payment = Payment.objects.create(
        order=order,
        payment_method='MANUAL_UPI',
        amount=order.total_amount,
        utr_number=utr_number,
        payer_upi_id=payer_upi_id,
        payer_name=payer_name,
        payment_screenshot=screenshot,
        status='PENDING'
    )

    # Transition order state to PAYMENT_VERIFICATION
    order.payment_status = 'SUBMITTED'
    order.status = 'PAYMENT_VERIFICATION'
    order.save()

    # Log to OrderStatusHistory
    OrderStatusHistory.objects.create(
        order=order,
        status='PAYMENT_VERIFICATION',
        comment=f"Customer submitted UPI transaction details (UTR: {utr_number}). Pending manual admin verification.",
        customer_visible=True
    )

    # In-app notification
    Notification.objects.create(
        user=order.user,
        order=order,
        title="Payment Submitted for Verification",
        message=f"UTR #{utr_number} for Order #{order.order_number} has been submitted. Our team will verify the payment against our bank records and confirm your order.",
        notification_type='PAYMENT_VERIFIED'
    )

    messages.success(request, "Payment details submitted! Our verification team is confirming your transaction with our bank account.")
    return redirect('payments:payment_success', order_number=order.order_number)


@login_required
def payment_success_view(request, order_number):
    """
    Shows payment submission confirmation, verification status, and order details.
    """
    order = get_object_or_404(Order, order_number=order_number)

    if order.user != request.user and not (request.user.is_staff or request.user.is_pocket_admin):
        return HttpResponseForbidden("You are not authorized to view this page.")

    payment = order.latest_payment
    return render(request, 'payments/payment_success.html', {
        'order': order,
        'payment': payment,
    })

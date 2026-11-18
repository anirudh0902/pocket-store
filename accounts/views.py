from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from .models import User, CustomerAddress
from orders.models import Order, Cart


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not email or not password or not first_name:
            messages.error(request, "First name, email, and password are required.")
            return render(request, 'accounts/register.html')

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html')

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email address already exists. Please log in.")
            return render(request, 'accounts/register.html')

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            is_customer=True
        )

        # Merge guest cart to user cart if exists
        session_key = request.session.session_key
        if session_key:
            guest_cart = Cart.objects.filter(session_key=session_key).first()
            if guest_cart:
                user_cart, _ = Cart.objects.get_or_create(user=user)
                for item in guest_cart.items.all():
                    existing_item = user_cart.items.filter(product=item.product, variant=item.variant).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        item.cart = user_cart
                        item.save()
                guest_cart.delete()

        login(request, user)
        messages.success(request, f"Welcome to POCKET, {user.first_name}! Your account has been created.")
        return redirect('core:home')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        login_id = request.POST.get('login_id', '').strip() # can be email or username
        password = request.POST.get('password', '')

        user = None
        # Try finding by email first
        try:
            found_user = User.objects.filter(email__iexact=login_id).first()
            if found_user:
                user = authenticate(request, username=found_user.username, password=password)
        except Exception:
            pass

        if not user:
            # Try finding by username
            user = authenticate(request, username=login_id, password=password)

        if user is not None:
            login(request, user)
            
            # Merge guest cart to user cart
            session_key = request.session.session_key
            if session_key:
                guest_cart = Cart.objects.filter(session_key=session_key).first()
                if guest_cart:
                    user_cart, _ = Cart.objects.get_or_create(user=user)
                    for item in guest_cart.items.all():
                        existing_item = user_cart.items.filter(product=item.product, variant=item.variant).first()
                        if existing_item:
                            existing_item.quantity += item.quantity
                            existing_item.save()
                        else:
                            item.cart = user_cart
                            item.save()
                    guest_cart.delete()

            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:home')
        else:
            messages.error(request, "Invalid email/username or password. Please try again.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('core:home')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        if first_name:
            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = phone_number
            user.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "First name cannot be empty.")

    recent_orders = user.orders.order_by('-created_at')[:3]
    addresses = user.addresses.all()[:2]
    return render(request, 'accounts/profile.html', {
        'recent_orders': recent_orders,
        'addresses': addresses,
    })


@login_required
def address_list_view(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_create_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        alternate_phone = request.POST.get('alternate_phone', '').strip()
        address_line_1 = request.POST.get('address_line_1', '').strip()
        address_line_2 = request.POST.get('address_line_2', '').strip()
        landmark = request.POST.get('landmark', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        address_type = request.POST.get('address_type', 'HOME')
        is_default = request.POST.get('is_default') == 'on'

        if not full_name or not phone_number or not address_line_1 or not city or not state or not pincode:
            messages.error(request, "Please fill in all mandatory address fields.")
            return render(request, 'accounts/address_form.html')

        # If it's the user's first address, set as default automatically
        if not request.user.addresses.exists():
            is_default = True

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
            address_type=address_type,
            is_default=is_default
        )
        messages.success(request, "Delivery address added successfully.")
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('accounts:address_list')

    return render(request, 'accounts/address_form.html', {'title': 'Add New Address'})


@login_required
def address_edit_view(request, pk):
    address = get_object_or_404(CustomerAddress, pk=pk, user=request.user)

    if request.method == 'POST':
        address.full_name = request.POST.get('full_name', '').strip()
        address.phone_number = request.POST.get('phone_number', '').strip()
        address.alternate_phone = request.POST.get('alternate_phone', '').strip()
        address.address_line_1 = request.POST.get('address_line_1', '').strip()
        address.address_line_2 = request.POST.get('address_line_2', '').strip()
        address.landmark = request.POST.get('landmark', '').strip()
        address.city = request.POST.get('city', '').strip()
        address.state = request.POST.get('state', '').strip()
        address.pincode = request.POST.get('pincode', '').strip()
        address.address_type = request.POST.get('address_type', 'HOME')
        address.is_default = request.POST.get('is_default') == 'on'
        address.save()

        messages.success(request, "Delivery address updated successfully.")
        return redirect('accounts:address_list')

    return render(request, 'accounts/address_form.html', {'address': address, 'title': 'Edit Address'})


@login_required
def address_delete_view(request, pk):
    address = get_object_or_404(CustomerAddress, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address removed successfully.")
        return redirect('accounts:address_list')
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


@login_required
@require_POST
def address_set_default_view(request, pk):
    address = get_object_or_404(CustomerAddress, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, f"Set {address.city} as default delivery address.")
    return redirect('accounts:address_list')


@login_required
def my_orders_view(request):
    """
    Shows all orders for the currently authenticated customer only.
    """
    orders = request.user.orders.order_by('-created_at').prefetch_related('items')
    return render(request, 'accounts/my_orders.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    """
    Shows specific order details, payment status, tracking details,
    and customer-visible status history.
    Strictly isolated: customer can ONLY view their own orders!
    """
    order = get_object_or_404(Order, order_number=order_number)
    
    # Permission check: must be the order's owner or staff
    if order.user != request.user and not (request.user.is_staff or request.user.is_pocket_admin):
        return HttpResponseForbidden("You are not authorized to view this order.")

    status_history = order.status_history.filter(customer_visible=True).order_by('created_at')
    
    return render(request, 'accounts/order_detail.html', {
        'order': order,
        'status_history': status_history,
    })

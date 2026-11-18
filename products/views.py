from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Category, ProductVariant, ProductReview
from orders.models import OrderItem


def product_list_view(request):
    """
    Product catalogue with category filters, price filters, sorting, search, and pagination.
    Never displays fake discounts or fake ratings.
    """
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'variants', 'reviews')

    # Category Filter
    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=current_category)

    # Search Query
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(specifications__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Special Quick Filters
    filter_type = request.GET.get('filter')
    if filter_type == 'bestsellers':
        products = products.filter(is_bestseller=True)
    elif filter_type == 'trending':
        products = products.filter(is_trending=True)
    elif filter_type == 'discount':
        products = products.filter(original_price__gt=models.F('selling_price'))

    # Price Range Filters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and min_price.isdigit():
        products = products.filter(selling_price__gte=float(min_price))
    if max_price and max_price.isdigit():
        products = products.filter(selling_price__lte=float(max_price))

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('selling_price')
    elif sort == 'price_desc':
        products = products.order_by('-selling_price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')

    # Pagination (12 products per page)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')

    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'current_category': current_category,
        'all_categories': all_categories,
        'query': query,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'filter_type': filter_type,
        'total_count': products.count(),
    })


def category_list_view(request):
    """
    Visual overview of all active product categories.
    """
    categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')
    return render(request, 'products/category_list.html', {'categories': categories})


def category_products_view(request, slug):
    """
    Dedicated view for a specific category.
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True).select_related('category').prefetch_related('images')
    
    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('selling_price')
    elif sort == 'price_desc':
        products = products.order_by('-selling_price')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/category_products.html', {
        'category': category,
        'page_obj': page_obj,
        'sort': sort,
    })


def product_detail_view(request, slug):
    """
    Comprehensive product details view.
    Displays images, pricing, variant selectors (sizes, colors), genuine reviews, and related products.
    """
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'variants', 'reviews__user'),
        slug=slug,
        is_active=True
    )

    # Distinct sizes & colors available for this product
    available_sizes = product.variants.filter(is_active=True, stock_quantity__gt=0).values_list('size', flat=True).distinct()
    available_colors = product.variants.filter(is_active=True, stock_quantity__gt=0).values('color', 'color_code').distinct()

    # Parse specifications lines
    specs_list = []
    if product.specifications:
        for line in product.specifications.split('\n'):
            line = line.strip()
            if line:
                if ':' in line:
                    k, v = line.split(':', 1)
                    specs_list.append((k.strip(), v.strip()))
                elif '|' in line:
                    for sub in line.split('|'):
                        if ':' in sub:
                            k, v = sub.split(':', 1)
                            specs_list.append((k.strip(), v.strip()))
                        else:
                            specs_list.append((sub.strip(), ''))
                else:
                    specs_list.append((line, ''))

    # Approved genuine reviews
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk).prefetch_related('images')[:4]

    # Check if user already reviewed or has ordered this product
    has_purchased = False
    user_review = None
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__payment_status='VERIFIED'
        ).exists()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'specs_list': specs_list,
        'available_sizes': available_sizes,
        'available_colors': available_colors,
        'reviews': reviews,
        'related_products': related_products,
        'has_purchased': has_purchased,
        'user_review': user_review,
    })


@login_required
def add_review_view(request, product_id):
    """
    Submits a genuine customer review.
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 5))
            if rating < 1 or rating > 5:
                rating = 5
        except (ValueError, TypeError):
            rating = 5

        review_text = request.POST.get('review_text', '').strip()

        # Check if verified purchase
        is_verified = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__payment_status='VERIFIED'
        ).exists()

        ProductReview.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'review_text': review_text,
                'is_verified_purchase': is_verified,
                'is_approved': True,  # Genuine direct user review
            }
        )

        messages.success(request, "Thank you for sharing your genuine review!")
        return redirect('products:product_detail', slug=product.slug)

    return redirect('products:product_detail', slug=product.slug)

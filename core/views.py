from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product, Category
from .models import ContactInquiry, NewsletterSubscriber


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Featured categories (clothing departments & essentials)
        ctx['featured_categories'] = Category.objects.filter(is_active=True).order_by('display_order', 'name')[:14]
        
        # Products sections (active products only)
        base_qs = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
        ctx['trending_products'] = base_qs.filter(is_trending=True)[:8]
        ctx['bestseller_products'] = base_qs.filter(is_bestseller=True)[:8]
        ctx['recent_products'] = base_qs.order_by('-created_at')[:8]
        
        # If no specific flags yet, fallback cleanly to recent
        if not ctx['trending_products']:
            ctx['trending_products'] = base_qs[:8]
        if not ctx['bestseller_products']:
            ctx['bestseller_products'] = base_qs.order_by('selling_price')[:8]

        return ctx


class AboutUsView(TemplateView):
    template_name = 'core/about_us.html'


class ContactUsView(TemplateView):
    template_name = 'core/contact_us.html'

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        if not name or not email or not subject or not message_text:
            messages.error(request, "Please fill in all required fields.")
            return render(request, self.template_name, {'name': name, 'email': email, 'phone': phone, 'subject': subject, 'message': message_text})

        ContactInquiry.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text
        )
        messages.success(request, "Thank you for contacting POCKET! Our team will respond to your inquiry shortly.")
        return redirect('core:contact_us')


class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy_policy.html'


class TermsConditionsView(TemplateView):
    template_name = 'core/terms_conditions.html'


class ShippingPolicyView(TemplateView):
    template_name = 'core/shipping_policy.html'


class CancellationPolicyView(TemplateView):
    template_name = 'core/cancellation_policy.html'


class ReturnsPolicyView(TemplateView):
    template_name = 'core/returns_policy.html'


@require_POST
def newsletter_signup_view(request):
    email = request.POST.get('email', '').strip().lower()
    if email:
        obj, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if created:
            messages.success(request, "Thank you for subscribing to POCKET special fashion offers!")
        else:
            messages.info(request, "You are already subscribed to our newsletter.")
    else:
        messages.error(request, "Please provide a valid email address.")
    
    # Redirect back to referring page or home
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'core:home')

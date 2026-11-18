from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutUsView.as_view(), name='about_us'),
    path('contact/', views.ContactUsView.as_view(), name='contact_us'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms/', views.TermsConditionsView.as_view(), name='terms_and_conditions'),
    path('shipping-policy/', views.ShippingPolicyView.as_view(), name='shipping_policy'),
    path('cancellation-policy/', views.CancellationPolicyView.as_view(), name='cancellation_policy'),
    path('returns-policy/', views.ReturnsPolicyView.as_view(), name='returns_policy'),
    path('newsletter-signup/', views.newsletter_signup_view, name='newsletter_signup'),
]

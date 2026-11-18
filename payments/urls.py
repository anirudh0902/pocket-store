from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<str:order_number>/', views.upi_payment_view, name='upi_payment'),
    path('submit/<str:order_number>/', views.submit_payment_view, name='submit_payment'),
    path('success/<str:order_number>/', views.payment_success_view, name='payment_success'),
]

from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Dashboard Overview
    path('', views.dashboard_overview_view, name='dashboard'),

    # Product Management
    path('products/', views.admin_product_list_view, name='product_list'),
    path('products/create/', views.admin_product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.admin_product_edit_view, name='product_edit'),
    path('products/<int:pk>/toggle-status/', views.admin_product_toggle_view, name='product_toggle'),
    path('products/<int:pk>/delete/', views.admin_product_delete_view, name='product_delete'),

    # Category Management
    path('categories/', views.admin_category_list_view, name='category_list'),
    path('categories/create/', views.admin_category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.admin_category_edit_view, name='category_edit'),
    path('categories/<int:pk>/delete/', views.admin_category_delete_view, name='category_delete'),

    # Supplier Management (Internal & Private)
    path('suppliers/', views.admin_supplier_list_view, name='supplier_list'),
    path('suppliers/create/', views.admin_supplier_create_view, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.admin_supplier_edit_view, name='supplier_edit'),

    # Order Management & Fulfillment
    path('orders/', views.admin_order_list_view, name='order_list'),
    path('orders/<str:order_number>/', views.admin_order_detail_view, name='order_detail'),
    path('orders/<str:order_number>/update-status/', views.admin_order_update_status_view, name='order_update_status'),
    path('orders/<str:order_number>/supplier-fulfillment/', views.admin_order_supplier_fulfillment_view, name='order_supplier_fulfillment'),
    path('orders/<str:order_number>/shipping-dispatch/', views.admin_order_shipping_dispatch_view, name='order_shipping_dispatch'),
    path('orders/<str:order_number>/update-expenses/', views.admin_order_expenses_update_view, name='order_update_expenses'),

    # Payment Verification
    path('payments/', views.admin_payment_list_view, name='payment_list'),
    path('payments/<int:pk>/approve/', views.admin_payment_approve_view, name='payment_approve'),
    path('payments/<int:pk>/reject/', views.admin_payment_reject_view, name='payment_reject'),

    # Profit & Financial Reports
    path('reports/', views.admin_financial_reports_view, name='reports'),

    # Store Settings & UPI Configuration
    path('settings/', views.admin_settings_view, name='settings'),
]

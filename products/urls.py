from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('categories/', views.category_list_view, name='category_list'),
    path('category/<slug:slug>/', views.category_products_view, name='category_products'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('product/<int:product_id>/review/', views.add_review_view, name='add_review'),
]

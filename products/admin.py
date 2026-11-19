from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, ProductReview


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order', 'is_active', 'active_products_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order', 'is_active')
    ordering = ('display_order', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'selling_price', 'original_price', 'stock_quantity', 'is_active', 'is_featured', 'is_trending', 'is_bestseller')
    list_filter = ('category', 'is_active', 'is_featured', 'is_trending', 'is_bestseller', 'created_at')
    search_fields = ('name', 'description', 'specifications')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('selling_price', 'stock_quantity', 'is_active')
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'stock_quantity', 'is_active')
    list_filter = ('is_active', 'size')
    search_fields = ('product__name', 'color', 'size')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'display_order')
    list_filter = ('is_primary',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified_purchase', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__username', 'review_text')

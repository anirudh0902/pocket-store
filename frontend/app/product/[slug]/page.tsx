'use client';

import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { fetchProductBySlug } from '../../../lib/api';
import { ProductDetail, ProductVariant } from '../../../lib/types';
import { useCart } from '../../../lib/cart-context';
import { Star, Truck, RefreshCw, ShieldCheck, ShoppingBag, Zap, ChevronRight } from 'lucide-react';

interface ProductPageProps {
  params: {
    slug: string;
  };
}

export default function ProductDetailPage({ params }: ProductPageProps) {
  const router = useRouter();
  const { addItem, isLoading: cartLoading } = useCart();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedImageIndex, setSelectedImageIndex] = useState<number>(0);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [quantity, setQuantity] = useState<number>(1);
  const [addingToCart, setAddingToCart] = useState<boolean>(false);

  useEffect(() => {
    async function loadProduct() {
      try {
        setLoading(true);
        const data = await fetchProductBySlug(params.slug);
        setProduct(data);
        if (data && data.variants && data.variants.length > 0) {
          // Default to first available in-stock variant
          const inStock = data.variants.find((v) => v.is_in_stock) || data.variants[0];
          setSelectedVariant(inStock);
        }
      } catch (err) {
        console.error('Error loading product:', err);
      } finally {
        setLoading(false);
      }
    }
    loadProduct();
  }, [params.slug]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <div className="inline-block w-8 h-8 border-4 border-[#0B162C] border-t-[#F7892A] rounded-full animate-spin mb-4" />
        <p className="text-sm font-semibold text-slate-600">Loading product details...</p>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h2 className="text-2xl font-bold text-slate-800">Product Not Found</h2>
        <p className="text-xs text-slate-500 mt-2">The product you are looking for does not exist or has been moved.</p>
        <Link
          href="/category/all"
          className="mt-6 inline-block px-6 py-2.5 bg-[#0B162C] text-white text-xs font-bold rounded-lg hover:bg-[#16284D]"
        >
          Return to Shop
        </Link>
      </div>
    );
  }

  const images = product.images && product.images.length > 0
    ? product.images.map((img) => img.image_url)
    : ['/pocket_logo.jpg'];

  const handleAddToCart = async () => {
    if (!product.is_in_stock) return;
    setAddingToCart(true);
    await addItem(product.id, selectedVariant ? selectedVariant.id : null, quantity);
    setAddingToCart(false);
  };

  const handleBuyNow = async () => {
    if (!product.is_in_stock) return;
    setAddingToCart(true);
    const success = await addItem(product.id, selectedVariant ? selectedVariant.id : null, quantity);
    setAddingToCart(false);
    if (success) {
      router.push('/checkout');
    }
  };

  const sellingPrice = Math.round(parseFloat(product.selling_price));
  const originalPrice = Math.round(parseFloat(product.original_price));
  const savings = originalPrice > sellingPrice ? originalPrice - sellingPrice : 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumbs */}
      <nav className="flex items-center space-x-2 text-xs text-slate-500 mb-6">
        <Link href="/" className="hover:text-[#F7892A]">Home</Link>
        <span>/</span>
        <Link href={`/category/${product.category?.slug || 'all'}`} className="hover:text-[#F7892A]">
          {product.category?.name || 'Category'}
        </Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold line-clamp-1">{product.name}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
        {/* Left Column: Image Gallery (5 cols) */}
        <div className="lg:col-span-6 flex flex-col-reverse sm:flex-row gap-4">
          {/* Thumbnails */}
          {images.length > 1 && (
            <div className="flex sm:flex-col gap-2 overflow-x-auto sm:overflow-y-auto sm:max-h-[550px] pb-2 sm:pb-0">
              {images.map((imgUrl, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedImageIndex(idx)}
                  className={`relative w-16 h-20 sm:w-20 sm:h-24 rounded-lg overflow-hidden border-2 flex-shrink-0 transition-all ${
                    selectedImageIndex === idx ? 'border-[#F7892A] shadow-md' : 'border-slate-200 opacity-70 hover:opacity-100'
                  }`}
                >
                  <Image
                    src={imgUrl}
                    alt={`${product.name} thumbnail ${idx + 1}`}
                    fill
                    className="object-cover object-top"
                  />
                </button>
              ))}
            </div>
          )}

          {/* Main Hero Image */}
          <div className="relative flex-1 aspect-[3/4] sm:min-h-[550px] bg-slate-100 rounded-2xl overflow-hidden border border-slate-200">
            <Image
              src={images[selectedImageIndex] || images[0]}
              alt={product.name}
              fill
              priority
              sizes="(max-width: 1024px) 100vw, 50vw"
              className="object-cover object-top"
            />
            {product.has_discount && product.discount_percentage > 0 && (
              <span className="absolute top-4 left-4 bg-[#F7892A] text-white text-xs font-black px-2.5 py-1 rounded shadow-md">
                {product.discount_percentage}% OFF
              </span>
            )}
          </div>
        </div>

        {/* Right Column: Product Info & Actions (6 cols) */}
        <div className="lg:col-span-6 space-y-6">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-[#F7892A]">
              {product.category?.name || 'Exclusive Drop'}
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-[#0B162C] tracking-tight mt-1 leading-snug">
              {product.name}
            </h1>

            {/* Rating */}
            {product.average_rating > 0 && (
              <div className="flex items-center space-x-2 mt-2">
                <div className="flex items-center space-x-1 bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-0.5 rounded text-xs font-bold">
                  <span>{product.average_rating.toFixed(1)}</span>
                  <Star size={12} className="fill-emerald-700 text-emerald-700" />
                </div>
                <span className="text-xs text-slate-500">
                  Based on {product.reviews_count || 12} verified ratings
                </span>
              </div>
            )}
          </div>

          {/* Price Box */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 space-y-1">
            <div className="flex items-baseline space-x-3">
              <span className="text-3xl font-black text-[#0B162C]">
                ₹{sellingPrice}
              </span>
              {originalPrice > sellingPrice && (
                <span className="text-base text-slate-400 line-through">
                  ₹{originalPrice}
                </span>
              )}
              {savings > 0 && (
                <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
                  Save ₹{savings}
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-500">
              Inclusive of all taxes. Free shipping on orders above ₹999.
            </p>
          </div>

          {/* Variants: Size Selector */}
          {product.variants && product.variants.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-800">
                  Select Size {selectedVariant && `(Size: ${selectedVariant.size})`}
                </span>
                <span className="text-slate-400 font-medium">Standard Indian Fit</span>
              </div>

              <div className="flex flex-wrap gap-2.5">
                {product.variants.map((v) => (
                  <button
                    key={v.id}
                    onClick={() => setSelectedVariant(v)}
                    disabled={!v.is_in_stock}
                    className={`min-w-[50px] h-11 px-3 rounded-lg text-xs font-bold border transition-all flex flex-col items-center justify-center ${
                      selectedVariant?.id === v.id
                        ? 'border-[#0B162C] bg-[#0B162C] text-white shadow-sm'
                        : v.is_in_stock
                        ? 'border-slate-300 bg-white text-slate-800 hover:border-[#0B162C]'
                        : 'border-slate-200 bg-slate-100 text-slate-400 line-through cursor-not-allowed'
                    }`}
                  >
                    <span>{v.size}</span>
                    {v.color && <span className="text-[9px] font-normal opacity-80">{v.color}</span>}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Quantity Selector */}
          <div className="flex items-center space-x-4">
            <span className="text-xs font-bold text-slate-800">Quantity:</span>
            <div className="flex items-center border border-slate-300 rounded-lg overflow-hidden bg-white">
              <button
                type="button"
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="w-8 h-8 flex items-center justify-center text-slate-600 hover:bg-slate-100 font-bold"
              >
                -
              </button>
              <span className="w-10 text-center text-xs font-bold text-slate-800">
                {quantity}
              </span>
              <button
                type="button"
                onClick={() => setQuantity(quantity + 1)}
                className="w-8 h-8 flex items-center justify-center text-slate-600 hover:bg-slate-100 font-bold"
              >
                +
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
            <button
              onClick={handleAddToCart}
              disabled={!product.is_in_stock || addingToCart || cartLoading}
              className="py-3.5 px-6 rounded-xl bg-white border-2 border-[#0B162C] text-[#0B162C] hover:bg-slate-50 font-bold text-sm flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
            >
              <ShoppingBag size={18} />
              <span>{addingToCart ? 'Adding...' : 'Add to Bag'}</span>
            </button>

            <button
              onClick={handleBuyNow}
              disabled={!product.is_in_stock || addingToCart || cartLoading}
              className="py-3.5 px-6 rounded-xl bg-[#F7892A] hover:bg-[#E2761A] text-white font-bold text-sm shadow-pocket-orange flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
            >
              <Zap size={18} />
              <span>Buy Now (UPI)</span>
            </button>
          </div>

          {/* Guarantees Box */}
          <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50 divide-y divide-slate-200/60 text-xs">
            <div className="flex items-center space-x-3 py-2">
              <Truck size={18} className="text-[#F7892A]" />
              <div>
                <span className="font-bold text-slate-800">Fast Express Shipping:</span>
                <span className="text-slate-500 ml-1">Dispatched within 24 hours. Delivered in 3-5 business days.</span>
              </div>
            </div>
            <div className="flex items-center space-x-3 py-2">
              <RefreshCw size={18} className="text-[#F7892A]" />
              <div>
                <span className="font-bold text-slate-800">7-Day Free Size Exchange:</span>
                <span className="text-slate-500 ml-1">Wrong size? We will exchange it at zero extra charge.</span>
              </div>
            </div>
            <div className="flex items-center space-x-3 py-2">
              <ShieldCheck size={18} className="text-[#F7892A]" />
              <div>
                <span className="font-bold text-slate-800">Secure Verified UPI Payment:</span>
                <span className="text-slate-500 ml-1">Supports PhonePe, Google Pay, BHIM, and Paytm.</span>
              </div>
            </div>
          </div>

          {/* Product Description */}
          <div className="pt-4 border-t border-slate-200 space-y-3">
            <h3 className="text-sm font-bold text-[#0B162C] uppercase tracking-wider">
              Product Overview
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-line">
              {product.description}
            </p>
          </div>

          {/* Specifications */}
          {product.specifications && (
            <div className="pt-4 border-t border-slate-200 space-y-3">
              <h3 className="text-sm font-bold text-[#0B162C] uppercase tracking-wider">
                Fabric & Specifications
              </h3>
              <div className="bg-slate-50 rounded-lg p-3 text-xs text-slate-700 whitespace-pre-line leading-relaxed border border-slate-200/70">
                {product.specifications}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

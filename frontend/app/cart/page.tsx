'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useCart } from '../../lib/cart-context';
import { Trash2, ArrowRight, ShoppingBag, ShieldCheck, Truck } from 'lucide-react';

export default function CartPage() {
  const router = useRouter();
  const { cart, isLoading, updateItem, removeItem } = useCart();

  if (isLoading && !cart) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="inline-block w-8 h-8 border-4 border-[#0B162C] border-t-[#F7892A] rounded-full animate-spin mb-4" />
        <p className="text-sm font-semibold text-slate-600">Loading your shopping bag...</p>
      </div>
    );
  }

  const items = cart?.items || [];

  if (items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto text-slate-400">
          <ShoppingBag size={40} />
        </div>
        <h2 className="text-2xl font-black text-[#0B162C]">Your Bag is Empty</h2>
        <p className="text-xs text-slate-500 max-w-sm mx-auto">
          Looks like you haven’t added any items yet. Discover our latest collection of oversized tees and cargo pants at direct prices!
        </p>
        <Link
          href="/category/all"
          className="inline-block px-7 py-3 rounded-xl bg-[#0B162C] text-white font-bold text-xs hover:bg-[#16284D] transition-colors shadow-sm"
        >
          Explore Collection
        </Link>
      </div>
    );
  }

  const subtotal = parseFloat(cart?.subtotal || '0');
  const shippingFee = parseFloat(cart?.shipping_fee || '0');
  const totalAmount = parseFloat(cart?.total_amount || '0');
  const freeShippingThreshold = parseFloat(cart?.free_shipping_threshold || '999');
  const freeShippingRemaining = parseFloat(cart?.free_shipping_remaining || '0');
  const qualifiesFreeShipping = cart?.qualifies_for_free_shipping;

  const progressPercent = Math.min(100, Math.round((subtotal / freeShippingThreshold) * 100));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl sm:text-3xl font-black text-[#0B162C] tracking-tight mb-6">
        Shopping Bag ({cart?.total_items || 0} {cart?.total_items === 1 ? 'item' : 'items'})
      </h1>

      {/* Free Shipping Alert Bar */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-8">
        <div className="flex items-center justify-between text-xs font-semibold mb-2">
          <span className="flex items-center space-x-1.5 text-slate-800">
            <Truck size={16} className="text-[#F7892A]" />
            {qualifiesFreeShipping ? (
              <span className="text-emerald-700 font-bold">🎉 Congratulations! You have unlocked FREE Shipping!</span>
            ) : (
              <span>
                Add <strong className="text-[#0B162C]">₹{Math.round(freeShippingRemaining)}</strong> more to get <strong className="text-[#F7892A]">FREE Shipping</strong>
              </span>
            )}
          </span>
          <span className="text-slate-500">{progressPercent}%</span>
        </div>
        <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
          <div
            className="bg-[#F7892A] h-full transition-all duration-500 rounded-full"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Cart Items (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          {items.map((item) => {
            const product = item.product;
            const imgUrl = product.primary_image_url || '/pocket_logo.jpg';
            const unitPrice = Math.round(parseFloat(product.selling_price));
            const itemTotal = Math.round(parseFloat(item.total_price));

            return (
              <div
                key={item.id}
                className="bg-white border border-slate-200 rounded-xl p-4 flex gap-4 items-start sm:items-center hover:border-slate-300 transition-colors"
              >
                {/* Thumbnail */}
                <div className="relative w-20 h-24 sm:w-24 sm:h-28 rounded-lg overflow-hidden bg-slate-100 flex-shrink-0 border border-slate-200">
                  <Image
                    src={imgUrl}
                    alt={product.name}
                    fill
                    className="object-cover object-top"
                  />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    {product.category_name}
                  </span>
                  <Link href={`/product/${product.slug}`}>
                    <h3 className="text-sm font-bold text-[#0B162C] truncate hover:text-[#F7892A] transition-colors">
                      {product.name}
                    </h3>
                  </Link>

                  {item.variant && (
                    <div className="mt-1 flex items-center space-x-2 text-xs text-slate-500">
                      <span className="bg-slate-100 px-2 py-0.5 rounded font-semibold text-slate-700">
                        Size: {item.variant.size}
                      </span>
                      {item.variant.color && (
                        <span>• Color: {item.variant.color}</span>
                      )}
                    </div>
                  )}

                  <div className="mt-2 text-xs font-bold text-[#0B162C]">
                    ₹{unitPrice} each
                  </div>
                </div>

                {/* Quantity Controls & Total */}
                <div className="flex flex-col sm:flex-row items-end sm:items-center gap-3">
                  <div className="flex items-center border border-slate-200 rounded-lg overflow-hidden bg-white">
                    <button
                      type="button"
                      onClick={() => updateItem(item.id, Math.max(1, item.quantity - 1))}
                      className="w-7 h-7 flex items-center justify-center text-slate-600 hover:bg-slate-100 font-bold"
                    >
                      -
                    </button>
                    <span className="w-8 text-center text-xs font-bold text-slate-800">
                      {item.quantity}
                    </span>
                    <button
                      type="button"
                      onClick={() => updateItem(item.id, item.quantity + 1)}
                      className="w-7 h-7 flex items-center justify-center text-slate-600 hover:bg-slate-100 font-bold"
                    >
                      +
                    </button>
                  </div>

                  <div className="text-right min-w-[70px]">
                    <span className="text-sm font-black text-[#0B162C]">
                      ₹{itemTotal}
                    </span>
                  </div>

                  <button
                    onClick={() => removeItem(item.id)}
                    className="p-1.5 text-slate-400 hover:text-red-600 transition-colors"
                    title="Remove item"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Order Summary (4 cols) */}
        <div className="lg:col-span-4">
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 space-y-4 sticky top-28">
            <h3 className="text-base font-black text-[#0B162C] uppercase tracking-wide border-b border-slate-200 pb-3">
              Order Summary
            </h3>

            <div className="space-y-2.5 text-xs text-slate-600">
              <div className="flex justify-between">
                <span>Items Subtotal</span>
                <span className="font-bold text-slate-900">₹{Math.round(subtotal)}</span>
              </div>
              <div className="flex justify-between">
                <span>Estimated Shipping</span>
                {shippingFee === 0 ? (
                  <span className="font-bold text-emerald-600 uppercase">FREE</span>
                ) : (
                  <span className="font-bold text-slate-900">₹{Math.round(shippingFee)}</span>
                )}
              </div>
            </div>

            <div className="border-t border-slate-200 pt-3 flex justify-between items-baseline">
              <div>
                <span className="text-sm font-black text-[#0B162C]">Total Payable</span>
                <p className="text-[10px] text-slate-500">Includes all taxes</p>
              </div>
              <span className="text-2xl font-black text-[#0B162C]">
                ₹{Math.round(totalAmount)}
              </span>
            </div>

            <button
              onClick={() => router.push('/checkout')}
              className="w-full py-3.5 px-6 rounded-xl bg-[#F7892A] hover:bg-[#E2761A] text-white font-bold text-sm shadow-pocket-orange transition-all flex items-center justify-center space-x-2"
            >
              <span>Proceed to Checkout</span>
              <ArrowRight size={16} />
            </button>

            <div className="pt-2 flex items-center justify-center space-x-2 text-[11px] text-slate-500">
              <ShieldCheck size={14} className="text-emerald-600" />
              <span>Safe & Secure UPI Checkout</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

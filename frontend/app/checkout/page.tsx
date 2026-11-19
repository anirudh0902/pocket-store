'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useCart } from '../../lib/cart-context';
import { submitCheckout, CheckoutPayload } from '../../lib/api';
import { ShieldCheck, Truck, ArrowLeft, Lock, CheckCircle2 } from 'lucide-react';

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi', 'Jammu and Kashmir'
];

export default function CheckoutPage() {
  const router = useRouter();
  const { cart, emptyCart } = useCart();

  const [formData, setFormData] = useState<CheckoutPayload>({
    full_name: '',
    phone: '',
    street_address: '',
    apartment_suite: '',
    city: '',
    state: 'Delhi',
    postal_code: '',
    landmark: '',
    customer_notes: '',
  });

  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const items = cart?.items || [];
  const subtotal = parseFloat(cart?.subtotal || '0');
  const shippingFee = parseFloat(cart?.shipping_fee || '0');
  const totalAmount = parseFloat(cart?.total_amount || '0');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    // Basic frontend validations
    if (!formData.full_name.trim()) {
      setErrorMsg('Please enter your full name.');
      return;
    }
    const cleanPhone = formData.phone.replace(/[^0-9]/g, '');
    if (cleanPhone.length < 10) {
      setErrorMsg('Please enter a valid 10-digit mobile number.');
      return;
    }
    if (!formData.street_address.trim()) {
      setErrorMsg('Please enter your delivery street address.');
      return;
    }
    if (!formData.city.trim()) {
      setErrorMsg('Please enter your city.');
      return;
    }
    if (formData.postal_code.replace(/\s+/g, '').length < 5) {
      setErrorMsg('Please enter a valid PIN code.');
      return;
    }

    try {
      setSubmitting(true);
      const result = await submitCheckout({
        ...formData,
        phone: cleanPhone,
      });

      // Clear local cart state as order is placed
      await emptyCart();

      // Redirect to UPI payment step
      router.push(`/payment/${result.order.order_number}`);
    } catch (err: any) {
      console.error('Checkout error:', err);
      setErrorMsg(err.message || 'Failed to place order. Please check your details and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!cart || items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center space-y-4">
        <h2 className="text-2xl font-black text-[#0B162C]">Your Bag is Empty</h2>
        <p className="text-xs text-slate-500">Please add items to your cart before proceeding to checkout.</p>
        <Link
          href="/category/all"
          className="inline-block px-6 py-2.5 bg-[#0B162C] text-white font-bold text-xs rounded-lg hover:bg-[#16284D]"
        >
          Browse Collection
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <div className="flex items-center space-x-2 text-xs text-slate-500 mb-6">
        <Link href="/cart" className="flex items-center space-x-1 hover:text-[#F7892A]">
          <ArrowLeft size={14} />
          <span>Back to Bag</span>
        </Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">Secure Checkout</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
        {/* Left Column: Delivery Details Form (7 cols) */}
        <div className="lg:col-span-7">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm">
            <div className="flex items-center space-x-2 pb-5 border-b border-slate-100">
              <Truck size={20} className="text-[#F7892A]" />
              <h2 className="text-lg font-black text-[#0B162C] uppercase tracking-wide">
                Delivery Address
              </h2>
            </div>

            {errorMsg && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    required
                    value={formData.full_name}
                    onChange={handleChange}
                    placeholder="e.g. Rahul Sharma"
                    className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Mobile Number (for delivery SMS) *
                  </label>
                  <div className="flex">
                    <span className="inline-flex items-center px-3 text-xs font-bold text-slate-500 bg-slate-100 border border-r-0 border-slate-300 rounded-l-lg">
                      +91
                    </span>
                    <input
                      type="tel"
                      name="phone"
                      required
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder="9876543210"
                      className="w-full text-xs px-3.5 py-2.5 rounded-r-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Flat, House no., Building, Company, Apartment *
                </label>
                <input
                  type="text"
                  name="street_address"
                  required
                  value={formData.street_address}
                  onChange={handleChange}
                  placeholder="e.g. Flat 302, Sunrise Towers, MG Road"
                  className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    City / District *
                  </label>
                  <input
                    type="text"
                    name="city"
                    required
                    value={formData.city}
                    onChange={handleChange}
                    placeholder="e.g. Bangalore"
                    className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    State *
                  </label>
                  <select
                    name="state"
                    value={formData.state}
                    onChange={handleChange}
                    className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                  >
                    {INDIAN_STATES.map((st) => (
                      <option key={st} value={st}>
                        {st}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    PIN Code *
                  </label>
                  <input
                    type="text"
                    name="postal_code"
                    required
                    maxLength={6}
                    value={formData.postal_code}
                    onChange={handleChange}
                    placeholder="560001"
                    className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Landmark (Optional)
                </label>
                <input
                  type="text"
                  name="landmark"
                  value={formData.landmark}
                  onChange={handleChange}
                  placeholder="Near Metro Station, opposite park"
                  className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Delivery Instructions (Optional)
                </label>
                <textarea
                  name="customer_notes"
                  rows={2}
                  value={formData.customer_notes}
                  onChange={handleChange}
                  placeholder="Leave at security gate / Call before delivery"
                  className="w-full text-xs px-3.5 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                />
              </div>

              {/* Payment Method Banner */}
              <div className="pt-4 border-t border-slate-100">
                <div className="p-4 rounded-xl bg-orange-50/70 border border-orange-200/80 flex items-start space-x-3">
                  <CheckCircle2 size={18} className="text-[#F7892A] flex-shrink-0 mt-0.5" />
                  <div className="text-xs">
                    <span className="font-bold text-[#0B162C]">Payment Method: Verified Direct UPI</span>
                    <p className="text-slate-600 mt-0.5">
                      You will scan the official POCKET QR code or pay via PhonePe/GPay on the next screen and submit your 12-digit UTR reference for instant verification.
                    </p>
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-4 px-6 rounded-xl bg-[#F7892A] hover:bg-[#E2761A] text-white font-extrabold text-sm shadow-pocket-orange transition-all duration-200 flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                <Lock size={16} />
                <span>{submitting ? 'Creating Order...' : `Place Order & Pay ₹${Math.round(totalAmount)}`}</span>
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Order Items Summary (5 cols) */}
        <div className="lg:col-span-5">
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 space-y-4 sticky top-28">
            <h3 className="text-base font-black text-[#0B162C] uppercase tracking-wide border-b border-slate-200 pb-3">
              Items in Order ({items.length})
            </h3>

            <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
              {items.map((it) => (
                <div key={it.id} className="flex justify-between items-center text-xs">
                  <div className="flex-1 pr-3">
                    <p className="font-bold text-slate-800 line-clamp-1">{it.product.name}</p>
                    <p className="text-slate-400">
                      Qty: {it.quantity} {it.variant ? `• Size: ${it.variant.size}` : ''}
                    </p>
                  </div>
                  <span className="font-bold text-[#0B162C]">
                    ₹{Math.round(parseFloat(it.total_price))}
                  </span>
                </div>
              ))}
            </div>

            <div className="border-t border-slate-200 pt-3 space-y-2 text-xs text-slate-600">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span className="font-bold text-slate-800">₹{Math.round(subtotal)}</span>
              </div>
              <div className="flex justify-between">
                <span>Shipping</span>
                {shippingFee === 0 ? (
                  <span className="font-bold text-emerald-600 uppercase">FREE</span>
                ) : (
                  <span className="font-bold text-slate-800">₹{Math.round(shippingFee)}</span>
                )}
              </div>
              <div className="flex justify-between text-base font-black text-[#0B162C] border-t border-slate-200 pt-2">
                <span>Total Amount</span>
                <span>₹{Math.round(totalAmount)}</span>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-200/80 flex items-center justify-center space-x-2 text-[11px] text-slate-500">
              <ShieldCheck size={14} className="text-emerald-600" />
              <span>Safe 256-bit Encrypted Checkout</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

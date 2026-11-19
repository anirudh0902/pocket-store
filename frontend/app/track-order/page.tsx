'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { trackOrder, fetchOrderDetail } from '../../lib/api';
import { OrderDetail } from '../../lib/types';
import { Search, Truck, CheckCircle2, Clock, PackageCheck, AlertCircle, ArrowLeft } from 'lucide-react';

const STATUS_STEPS = [
  { key: 'PENDING', label: 'Order Placed' },
  { key: 'PAYMENT_VERIFIED', label: 'Payment Verified' },
  { key: 'PROCESSING', label: 'Packed & Ready' },
  { key: 'SHIPPED', label: 'Shipped' },
  { key: 'DELIVERED', label: 'Delivered' },
];

function TrackOrderContent() {
  const searchParams = useSearchParams();
  const urlOrderNumber = searchParams.get('order_number') || '';

  const [orderNumber, setOrderNumber] = useState<string>(urlOrderNumber);
  const [phone, setPhone] = useState<string>('');
  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (urlOrderNumber) {
      setOrderNumber(urlOrderNumber);
      // Attempt auto-lookup
      autoTrack(urlOrderNumber);
    }
  }, [urlOrderNumber]);

  const autoTrack = async (num: string) => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const data = await fetchOrderDetail(num);
      setOrder(data);
    } catch {
      // If direct fetch fails without phone verification, user will fill phone
    } finally {
      setLoading(false);
    }
  };

  const handleTrackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orderNumber.trim()) {
      setErrorMsg('Please enter your Order Number.');
      return;
    }

    try {
      setLoading(true);
      setErrorMsg(null);
      const data = phone.trim()
        ? await trackOrder(orderNumber.trim(), phone.trim())
        : await fetchOrderDetail(orderNumber.trim());
      setOrder(data);
    } catch (err: any) {
      console.error('Tracking error:', err);
      setErrorMsg(err.message || 'Could not find an order with this number and phone.');
      setOrder(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="text-center space-y-2 mb-8">
        <div className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-[#F7892A]">
          <Truck size={16} />
          <span>Live Tracking</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-[#0B162C]">
          Track Your Order
        </h1>
        <p className="text-xs text-slate-500">
          Enter your POCKET Order Reference Number and registered phone number.
        </p>
      </div>

      {/* Search Input Box */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm mb-8">
        <form onSubmit={handleTrackSubmit} className="grid grid-cols-1 sm:grid-cols-12 gap-3">
          <div className="sm:col-span-6">
            <input
              type="text"
              required
              value={orderNumber}
              onChange={(e) => setOrderNumber(e.target.value.toUpperCase())}
              placeholder="Order Number (e.g. PKT-202611...)"
              className="w-full text-xs font-mono uppercase px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
            />
          </div>
          <div className="sm:col-span-4">
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Registered Phone (optional)"
              className="w-full text-xs px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
            />
          </div>
          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full h-full py-3 px-4 rounded-xl bg-[#0B162C] hover:bg-[#16284D] text-white font-bold text-xs flex items-center justify-center space-x-1 transition-colors disabled:opacity-50"
            >
              <Search size={14} />
              <span>{loading ? '...' : 'Track'}</span>
            </button>
          </div>
        </form>

        {errorMsg && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-center space-x-2">
            <AlertCircle size={15} />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Order Results */}
      {order && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm space-y-8">
          {/* Status Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-200 gap-3">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Order Reference
              </span>
              <h2 className="text-xl font-black text-[#0B162C] font-mono">
                {order.order_number}
              </h2>
              <span className="text-xs text-slate-500">
                Placed on {new Date(order.created_at).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
              </span>
            </div>

            <div className="flex flex-col sm:items-end">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Status</span>
              <span className="inline-block mt-0.5 px-3 py-1 rounded-full text-xs font-bold bg-[#0B162C] text-white">
                {order.status_display}
              </span>
              <span className="text-[11px] font-semibold text-[#F7892A] mt-1">
                Payment: {order.payment_status_display}
              </span>
            </div>
          </div>

          {/* Timeline */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-6">
              Fulfillment Progress
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
              {STATUS_STEPS.map((step, idx) => {
                const isCurrent = order.status === step.key;
                return (
                  <div
                    key={step.key}
                    className={`p-3 rounded-xl border text-xs flex flex-col items-center justify-center space-y-1 ${
                      isCurrent
                        ? 'border-[#F7892A] bg-orange-50/60 font-bold text-[#0B162C]'
                        : 'border-slate-200 bg-slate-50 text-slate-500'
                    }`}
                  >
                    <div className="w-6 h-6 rounded-full bg-white border flex items-center justify-center text-[10px] font-bold">
                      {idx + 1}
                    </div>
                    <span>{step.label}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Items Summary */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              Items Ordered ({order.items.length})
            </h4>
            <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden">
              {order.items.map((it) => (
                <div key={it.id} className="p-3.5 flex justify-between items-center text-xs">
                  <div>
                    <p className="font-bold text-slate-800">{it.product_name}</p>
                    {it.variant_details && (
                      <p className="text-slate-500 mt-0.5">{it.variant_details}</p>
                    )}
                    <span className="text-slate-400">Qty: {it.quantity}</span>
                  </div>
                  <span className="font-bold text-[#0B162C]">
                    ₹{Math.round(parseFloat(it.total_price))}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Total */}
          <div className="flex justify-between items-baseline pt-4 border-t border-slate-200 text-sm">
            <span className="font-bold text-slate-700">Total Order Amount:</span>
            <span className="text-xl font-black text-[#0B162C]">
              ₹{Math.round(parseFloat(order.total_amount))}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function TrackOrderPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-4xl mx-auto px-4 py-20 text-center text-xs text-slate-500">
          Loading order tracker...
        </div>
      }
    >
      <TrackOrderContent />
    </Suspense>
  );
}

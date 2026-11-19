'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { fetchUPIDetails, submitUTR } from '../../../lib/api';
import { UPIDetails } from '../../../lib/types';
import { Copy, Check, ShieldCheck, Clock, CheckCircle2, ArrowRight, HelpCircle } from 'lucide-react';

interface PaymentPageProps {
  params: {
    order_number: string;
  };
}

export default function PaymentPage({ params }: PaymentPageProps) {
  const { order_number } = params;

  const [upiData, setUpiData] = useState<UPIDetails | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [copied, setCopied] = useState<boolean>(false);

  // UTR submission form state
  const [utrNumber, setUtrNumber] = useState<string>('');
  const [payerName, setPayerName] = useState<string>('');
  const [payerPhone, setPayerPhone] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [submittedSuccess, setSubmittedSuccess] = useState<boolean>(false);

  useEffect(() => {
    async function loadUPI() {
      try {
        setLoading(true);
        const data = await fetchUPIDetails(order_number);
        setUpiData(data);
      } catch (err: any) {
        console.error('Failed to load UPI details:', err);
        setErrorMsg('Could not fetch payment details for this order.');
      } finally {
        setLoading(false);
      }
    }
    loadUPI();
  }, [order_number]);

  const handleCopyUPI = () => {
    if (upiData?.upi_id) {
      navigator.clipboard.writeText(upiData.upi_id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const handleUTRSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    const cleanUtr = utrNumber.trim().toUpperCase();
    if (cleanUtr.length < 8 || cleanUtr.length > 25) {
      setErrorMsg('Please enter a valid 8 to 25 character UTR / Transaction reference number.');
      return;
    }
    if (!payerName.trim()) {
      setErrorMsg('Please enter the name on your bank/UPI account.');
      return;
    }

    try {
      setSubmitting(true);
      await submitUTR({
        order_number,
        utr_number: cleanUtr,
        payer_name: payerName.trim(),
        payer_phone: payerPhone.trim(),
      });
      setSubmittedSuccess(true);
    } catch (err: any) {
      console.error('UTR submission error:', err);
      setErrorMsg(err.message || 'Could not verify UTR. Please ensure it is accurate.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center">
        <div className="inline-block w-8 h-8 border-4 border-[#0B162C] border-t-[#F7892A] rounded-full animate-spin mb-4" />
        <p className="text-sm font-semibold text-slate-600">Generating secure UPI payment QR...</p>
      </div>
    );
  }

  if (submittedSuccess) {
    return (
      <div className="max-w-xl mx-auto px-4 sm:px-6 py-16">
        <div className="bg-white border border-emerald-200 rounded-3xl p-8 text-center space-y-6 shadow-sm">
          <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto shadow-sm">
            <CheckCircle2 size={36} />
          </div>

          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-widest text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
              UTR Reference Submitted
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-[#0B162C]">
              Payment Under Verification
            </h1>
            <p className="text-xs text-slate-600 max-w-md mx-auto leading-relaxed">
              Thank you! Your UTR <strong className="text-slate-800">#{utrNumber}</strong> has been logged for Order <strong className="text-slate-800">{order_number}</strong>.
            </p>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-left text-xs space-y-2.5">
            <div className="flex items-start space-x-2.5">
              <Clock size={16} className="text-[#F7892A] flex-shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-800">Verification in 15-30 minutes:</strong>
                <p className="text-slate-500">
                  Our finance team manually cross-verifies bank credits to ensure fraud protection. You will receive an SMS and WhatsApp confirmation as soon as verified.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-2.5">
              <ShieldCheck size={16} className="text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-800">Direct Dispatch:</strong>
                <p className="text-slate-500">
                  Your order is prepared at the factory warehouse for immediate dispatch upon confirmation.
                </p>
              </div>
            </div>
          </div>

          <div className="pt-2 flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              href={`/track-order?order_number=${encodeURIComponent(order_number)}`}
              className="px-6 py-3 rounded-xl bg-[#0B162C] hover:bg-[#16284D] text-white font-bold text-xs flex items-center justify-center space-x-2 transition-colors"
            >
              <span>Track Your Order</span>
              <ArrowRight size={14} />
            </Link>

            <Link
              href="/"
              className="px-6 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-colors"
            >
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const qrUrl = upiData?.upi_intent_url
    ? `https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=${encodeURIComponent(upiData.upi_intent_url)}`
    : '';

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="text-center space-y-2 mb-8">
        <span className="text-xs font-bold uppercase tracking-wider text-[#F7892A]">
          Step 2: Complete Payment
        </span>
        <h1 className="text-2xl sm:text-3xl font-black text-[#0B162C]">
          Scan & Pay via UPI
        </h1>
        <p className="text-xs text-slate-500">
          Order Reference: <strong className="text-[#0B162C] font-mono">{order_number}</strong>
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
        {/* Left Column: QR Code & UPI ID */}
        <div className="flex flex-col items-center text-center space-y-4 md:border-r md:border-slate-100 md:pr-8">
          <div className="bg-slate-50 p-3 rounded-2xl border-2 border-dashed border-[#F7892A]/50 relative">
            {qrUrl ? (
              <img
                src={qrUrl}
                alt="UPI Payment QR Code"
                width={210}
                height={210}
                className="rounded-xl"
              />
            ) : (
              <div className="w-[210px] h-[210px] flex items-center justify-center text-xs text-slate-400">
                Generating QR...
              </div>
            )}
          </div>

          <div className="space-y-1">
            <span className="text-xs text-slate-500 font-medium">Exact Amount to Pay:</span>
            <div className="text-3xl font-black text-[#0B162C]">
              ₹{upiData?.amount ? Math.round(parseFloat(upiData.amount)) : 0}
            </div>
          </div>

          {/* UPI ID Copy box */}
          <div className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 flex items-center justify-between text-xs">
            <div className="text-left min-w-0 pr-2">
              <span className="block text-[10px] font-bold text-slate-400 uppercase">POCKET Official UPI ID</span>
              <span className="font-mono font-bold text-slate-800 truncate block">
                {upiData?.upi_id || 'pocket@upi'}
              </span>
            </div>
            <button
              onClick={handleCopyUPI}
              className="px-3 py-1.5 rounded-lg bg-white border border-slate-300 hover:border-slate-400 text-slate-700 font-bold text-[11px] flex items-center space-x-1 transition-colors flex-shrink-0"
            >
              {copied ? <Check size={13} className="text-emerald-600" /> : <Copy size={13} />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </button>
          </div>

          {/* Quick UPI Intent Link for Mobile */}
          {upiData?.upi_intent_url && (
            <a
              href={upiData.upi_intent_url}
              className="w-full py-2.5 rounded-xl bg-slate-900 text-white font-bold text-xs text-center hover:bg-black transition-colors md:hidden"
            >
              Open in PhonePe / GPay / Paytm
            </a>
          )}
        </div>

        {/* Right Column: UTR Reference Form */}
        <div className="flex flex-col justify-between space-y-5">
          <div className="space-y-3">
            <h3 className="text-sm font-black text-[#0B162C] uppercase tracking-wide">
              Submit Bank UTR / Reference
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              After completing payment in your UPI app, find the 12-digit <strong>UTR / UPI Transaction ID</strong> in your payment details and enter it below.
            </p>

            {errorMsg && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleUTRSubmit} className="space-y-3.5 pt-1">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  12-Digit UTR / Transaction ID *
                </label>
                <input
                  type="text"
                  required
                  value={utrNumber}
                  onChange={(e) => setUtrNumber(e.target.value.toUpperCase())}
                  placeholder="e.g. 432109876543"
                  className="w-full text-xs font-mono uppercase px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Account Holder Name (as in UPI app) *
                </label>
                <input
                  type="text"
                  required
                  value={payerName}
                  onChange={(e) => setPayerName(e.target.value)}
                  placeholder="e.g. Rahul Sharma"
                  className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  UPI Phone Number (Optional)
                </label>
                <input
                  type="tel"
                  value={payerPhone}
                  onChange={(e) => setPayerPhone(e.target.value)}
                  placeholder="e.g. 9876543210"
                  className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3.5 px-6 rounded-xl bg-[#F7892A] hover:bg-[#E2761A] text-white font-extrabold text-xs shadow-pocket-orange transition-all duration-200 flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                <CheckCircle2 size={16} />
                <span>{submitting ? 'Verifying...' : 'Submit UTR & Confirm Order'}</span>
              </button>
            </form>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center space-x-2 text-[11px] text-slate-400">
            <ShieldCheck size={14} className="text-emerald-600 flex-shrink-0" />
            <span>Orders are strictly verified to prevent uncredited transactions.</span>
          </div>
        </div>
      </div>
    </div>
  );
}

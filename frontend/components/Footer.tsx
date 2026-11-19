import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ShieldCheck, RefreshCw, Truck, Award, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-[#0B162C] text-white pt-14 pb-8 border-t border-slate-800">
      {/* Trust & Guarantee Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12 border-b border-slate-800/80">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="flex flex-col items-center p-3">
            <div className="w-12 h-12 rounded-full bg-[#16284D] flex items-center justify-center text-[#F7892A] mb-3">
              <Truck size={24} />
            </div>
            <h4 className="font-bold text-sm text-slate-100">Free Fast Delivery</h4>
            <p className="text-xs text-slate-400 mt-1">On all prepaid orders over ₹999</p>
          </div>
          <div className="flex flex-col items-center p-3">
            <div className="w-12 h-12 rounded-full bg-[#16284D] flex items-center justify-center text-[#F7892A] mb-3">
              <RefreshCw size={24} />
            </div>
            <h4 className="font-bold text-sm text-slate-100">7-Day Easy Exchange</h4>
            <p className="text-xs text-slate-400 mt-1">Hassle-free size replacement</p>
          </div>
          <div className="flex flex-col items-center p-3">
            <div className="w-12 h-12 rounded-full bg-[#16284D] flex items-center justify-center text-[#F7892A] mb-3">
              <Award size={24} />
            </div>
            <h4 className="font-bold text-sm text-slate-100">100% Pure Combed Cotton</h4>
            <p className="text-xs text-slate-400 mt-1">Directly sourced premium fabrics</p>
          </div>
          <div className="flex flex-col items-center p-3">
            <div className="w-12 h-12 rounded-full bg-[#16284D] flex items-center justify-center text-[#F7892A] mb-3">
              <ShieldCheck size={24} />
            </div>
            <h4 className="font-bold text-sm text-slate-100">Verified UPI Payments</h4>
            <p className="text-xs text-slate-400 mt-1">PhonePe, Google Pay, Paytm & BHIM</p>
          </div>
        </div>
      </div>

      {/* Main Footer Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center space-x-3">
              <div className="relative w-12 h-12 rounded-lg overflow-hidden border border-slate-700 shadow-sm bg-white">
                <Image
                  src="/pocket_logo.jpg"
                  alt="POCKET Official Logo"
                  fill
                  className="object-cover"
                />
              </div>
              <div>
                <span className="text-2xl font-black tracking-tight text-white">
                  POCKET<span className="text-[#F7892A]">.</span>
                </span>
                <p className="text-xs uppercase tracking-wider text-slate-400 font-medium">
                  Fashion that fits your pocket.
                </p>
              </div>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed max-w-sm">
              POCKET brings you modern streetwear, premium oversized tees, structured polos, and durable cargo pants at genuine direct-from-manufacturer prices. Zero middleman markup, unmatched fabric longevity.
            </p>
            <div className="pt-2">
              <span className="inline-block bg-[#16284D] border border-slate-700 text-[#F7892A] text-xs font-semibold px-3 py-1.5 rounded-full">
                100% Made in India Fashion
              </span>
            </div>
          </div>

          {/* Categories */}
          <div>
            <h5 className="text-sm font-bold text-white uppercase tracking-wider mb-4 border-b border-[#F7892A] pb-1 w-max">
              Shop Categories
            </h5>
            <ul className="space-y-2 text-xs text-slate-300">
              <li>
                <Link href="/category/oversized-t-shirts" className="hover:text-[#F7892A] transition-colors">
                  Oversized T-shirts
                </Link>
              </li>
              <li>
                <Link href="/category/graphic-t-shirts" className="hover:text-[#F7892A] transition-colors">
                  Graphic T-shirts
                </Link>
              </li>
              <li>
                <Link href="/category/basic-t-shirts" className="hover:text-[#F7892A] transition-colors">
                  Basic T-shirts
                </Link>
              </li>
              <li>
                <Link href="/category/polo-t-shirts" className="hover:text-[#F7892A] transition-colors">
                  Polo T-shirts
                </Link>
              </li>
              <li>
                <Link href="/category/casual-shirts" className="hover:text-[#F7892A] transition-colors">
                  Casual Shirts
                </Link>
              </li>
              <li>
                <Link href="/category/joggers" className="hover:text-[#F7892A] transition-colors">
                  Joggers & Track Pants
                </Link>
              </li>
              <li>
                <Link href="/category/cargo-pants" className="hover:text-[#F7892A] transition-colors">
                  Cargo Pants
                </Link>
              </li>
            </ul>
          </div>

          {/* Quick Links */}
          <div>
            <h5 className="text-sm font-bold text-white uppercase tracking-wider mb-4 border-b border-[#F7892A] pb-1 w-max">
              Customer Support
            </h5>
            <ul className="space-y-2 text-xs text-slate-300">
              <li>
                <Link href="/track-order" className="hover:text-[#F7892A] transition-colors flex items-center space-x-1">
                  <span>Track Your Order</span>
                </Link>
              </li>
              <li>
                <Link href="/cart" className="hover:text-[#F7892A] transition-colors">
                  Shopping Bag
                </Link>
              </li>
              <li>
                <span className="text-slate-400">Shipping Policy (3-5 Days)</span>
              </li>
              <li>
                <span className="text-slate-400">Returns & Size Exchange</span>
              </li>
              <li>
                <span className="text-slate-400">UPI Payment Verification</span>
              </li>
            </ul>
          </div>

          {/* Secure Payments */}
          <div>
            <h5 className="text-sm font-bold text-white uppercase tracking-wider mb-4 border-b border-[#F7892A] pb-1 w-max">
              Verified UPI Payment
            </h5>
            <p className="text-xs text-slate-400 mb-3">
              Scan QR or pay directly via any verified UPI app:
            </p>
            <div className="flex flex-wrap gap-2 text-[11px] font-bold text-slate-200">
              <span className="bg-[#16284D] px-2.5 py-1 rounded border border-slate-700">PhonePe</span>
              <span className="bg-[#16284D] px-2.5 py-1 rounded border border-slate-700">Google Pay</span>
              <span className="bg-[#16284D] px-2.5 py-1 rounded border border-slate-700">Paytm</span>
              <span className="bg-[#16284D] px-2.5 py-1 rounded border border-slate-700">BHIM UPI</span>
            </div>
            <p className="text-[11px] text-slate-500 mt-3">
              Order confirmation is generated instantly upon UTR submission.
            </p>
          </div>
        </div>
      </div>

      {/* Copyright Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 border-t border-slate-800 text-center text-xs text-slate-500">
        <p>© {new Date().getFullYear()} POCKET. All Rights Reserved. Fashion that fits your pocket.</p>
      </div>
    </footer>
  );
}

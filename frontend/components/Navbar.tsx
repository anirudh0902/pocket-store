'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useCart } from '../lib/cart-context';
import { ShoppingBag, Search, Menu, X, User, Truck, ChevronDown } from 'lucide-react';

const CATEGORIES = [
  { name: 'Oversized T-shirts', slug: 'oversized-t-shirts' },
  { name: 'Graphic T-shirts', slug: 'graphic-t-shirts' },
  { name: 'Basic T-shirts', slug: 'basic-t-shirts' },
  { name: 'Polo T-shirts', slug: 'polo-t-shirts' },
  { name: 'Casual Shirts', slug: 'casual-shirts' },
  { name: 'Joggers', slug: 'joggers' },
  { name: 'Cargo Pants', slug: 'cargo-pants' },
];

export default function Navbar() {
  const router = useRouter();
  const { itemCount } = useCart();
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/category/all?search=${encodeURIComponent(searchQuery.trim())}`);
      setMobileMenuOpen(false);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm">
      {/* Top Announcement Bar */}
      <div className="bg-[#0B162C] text-white text-xs py-2 px-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="bg-[#F7892A] text-white font-bold px-2 py-0.5 rounded text-[10px] tracking-wide uppercase">
              Special Offer
            </span>
            <span>Free Shipping on all orders above ₹999 | 100% Cotton Guarantee</span>
          </div>
          <div className="hidden md:flex items-center space-x-6 text-slate-300">
            <Link href="/track-order" className="hover:text-white flex items-center space-x-1 transition-colors">
              <Truck size={14} className="text-[#F7892A]" />
              <span>Track Order</span>
            </Link>
            <span className="text-slate-500">|</span>
            <span className="text-slate-300">UPI Accepted (GPay, PhonePe, Paytm)</span>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo & Tagline */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="relative w-12 h-12 rounded-lg overflow-hidden border border-slate-100 shadow-sm">
              <Image
                src="/pocket_logo.jpg"
                alt="POCKET Logo"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-300"
              />
            </div>
            <div className="flex flex-col">
              <span className="text-2xl font-black tracking-tight text-[#0B162C]">
                POCKET<span className="text-[#F7892A]">.</span>
              </span>
              <span className="text-[10px] uppercase tracking-wider font-semibold text-slate-500">
                Fashion that fits your pocket
              </span>
            </div>
          </Link>

          {/* Desktop Search Bar */}
          <div className="hidden md:flex flex-1 max-w-md mx-8">
            <form onSubmit={handleSearchSubmit} className="relative w-full">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search Oversized Tees, Joggers, Cargos..."
                className="w-full pl-10 pr-4 py-2.5 text-sm rounded-full border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#0B162C] focus:border-transparent transition-all"
              />
              <Search className="absolute left-3.5 top-3 text-slate-400" size={17} />
              <button
                type="submit"
                className="absolute right-1.5 top-1.5 bg-[#0B162C] text-white hover:bg-[#16284D] px-3.5 py-1.5 rounded-full text-xs font-semibold transition-colors"
              >
                Search
              </button>
            </form>
          </div>

          {/* Right Actions */}
          <div className="flex items-center space-x-5">
            <Link
              href="/track-order"
              className="hidden lg:flex items-center space-x-1.5 text-sm font-medium text-slate-700 hover:text-[#0B162C] transition-colors"
            >
              <Truck size={18} className="text-slate-500" />
              <span>Track</span>
            </Link>

            <Link
              href="/cart"
              className="relative p-2 text-slate-800 hover:text-[#0B162C] transition-colors flex items-center space-x-1"
              aria-label="Shopping Cart"
            >
              <div className="relative">
                <ShoppingBag size={24} className="text-[#0B162C]" />
                {itemCount > 0 && (
                  <span className="absolute -top-1.5 -right-2 bg-[#F7892A] text-white text-[11px] font-bold w-5 h-5 rounded-full flex items-center justify-center shadow-sm animate-pulse">
                    {itemCount}
                  </span>
                )}
              </div>
              <span className="hidden sm:inline-block text-xs font-bold text-slate-700 ml-1">Bag</span>
            </Link>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-700 hover:text-black focus:outline-none"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Desktop Category Navigation Menu */}
        <nav className="hidden md:flex items-center space-x-8 border-t border-slate-100 py-3 text-sm font-semibold">
          <Link
            href="/category/all"
            className="text-slate-900 hover:text-[#F7892A] transition-colors font-bold flex items-center space-x-1"
          >
            <span>All Collection</span>
          </Link>
          {CATEGORIES.map((cat) => (
            <Link
              key={cat.slug}
              href={`/category/${cat.slug}`}
              className="text-slate-600 hover:text-[#0B162C] hover:border-b-2 hover:border-[#F7892A] pb-1 transition-all"
            >
              {cat.name}
            </Link>
          ))}
        </nav>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-slate-200 px-4 pt-3 pb-6 space-y-4">
          <form onSubmit={handleSearchSubmit} className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search men's fashion..."
              className="w-full pl-9 pr-4 py-2 text-sm rounded-lg border border-slate-200 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-[#0B162C]"
            />
            <Search className="absolute left-3 top-2.5 text-slate-400" size={16} />
          </form>

          <div className="divide-y divide-slate-100">
            <Link
              href="/category/all"
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2.5 text-sm font-bold text-[#F7892A]"
            >
              Explore Full Collection
            </Link>
            {CATEGORIES.map((cat) => (
              <Link
                key={cat.slug}
                href={`/category/${cat.slug}`}
                onClick={() => setMobileMenuOpen(false)}
                className="block py-2.5 text-sm font-medium text-slate-800 hover:text-[#F7892A]"
              >
                {cat.name}
              </Link>
            ))}
            <Link
              href="/track-order"
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2.5 text-sm font-medium text-slate-700 flex items-center space-x-2"
            >
              <Truck size={16} className="text-[#F7892A]" />
              <span>Track Your Order</span>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}

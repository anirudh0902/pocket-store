import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowRight, Sparkles, ShieldCheck, Zap } from 'lucide-react';

export default function HeroBanner() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-[#0B162C] via-[#0E1E3D] to-[#060D1B] text-white py-14 sm:py-20">
      {/* Decorative background glows */}
      <div className="absolute -top-24 -right-24 w-96 h-96 rounded-full bg-[#F7892A]/15 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-96 h-96 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Left Column: Headline and CTAs */}
          <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
            <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-md border border-white/15 px-3.5 py-1.5 rounded-full text-xs font-semibold text-[#F7892A]">
              <Sparkles size={14} />
              <span>DIRECT FACTORY SOURCED • GENUINE POCKET PRICING</span>
            </div>

            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] text-white">
              Everyday Fashion,{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#F7892A] to-orange-400">
                Honest Prices.
              </span>
            </h1>

            <p className="text-base sm:text-lg text-slate-300 max-w-xl mx-auto lg:mx-0 leading-relaxed">
              Premium 220 GSM combed cotton oversized tees, 6-pocket tactical utility cargos, and heavyweight French terry joggers — tailored for Indian weather and made for everyday wear.
            </p>

            {/* Quick Guarantees */}
            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-4 text-xs font-medium text-slate-300 pt-2">
              <div className="flex items-center space-x-1.5">
                <Zap size={14} className="text-[#F7892A]" />
                <span>Under ₹699 Catalog</span>
              </div>
              <span className="text-slate-600">•</span>
              <div className="flex items-center space-x-1.5">
                <ShieldCheck size={14} className="text-[#F7892A]" />
                <span>100% Bio-Washed Cotton</span>
              </div>
              <span className="text-slate-600">•</span>
              <div className="flex items-center space-x-1.5">
                <span className="text-[#F7892A] font-bold">₹0</span>
                <span>Delivery Over ₹999</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3.5 pt-4">
              <Link
                href="/category/oversized-t-shirts"
                className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-[#F7892A] hover:bg-[#E2761A] text-white font-bold text-sm shadow-pocket-orange transition-all duration-200 flex items-center justify-center space-x-2 group"
              >
                <span>Shop Oversized Tees</span>
                <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
              </Link>

              <Link
                href="/category/cargo-pants"
                className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-sm border border-white/20 transition-all duration-200 text-center"
              >
                Explore Cargo Pants
              </Link>
            </div>
          </div>

          {/* Right Column: Visual Brand Card */}
          <div className="lg:col-span-5 flex justify-center">
            <div className="relative w-full max-w-sm aspect-square bg-[#0B162C]/80 border-2 border-[#F7892A]/40 rounded-3xl p-6 shadow-2xl flex flex-col items-center justify-center text-center backdrop-blur-xl group hover:border-[#F7892A] transition-all duration-500">
              <div className="relative w-36 h-36 rounded-2xl overflow-hidden border-2 border-white/20 shadow-lg mb-4 bg-white">
                <Image
                  src="/pocket_logo.jpg"
                  alt="POCKET Brand Logo"
                  fill
                  priority
                  className="object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>

              <div className="space-y-1">
                <h3 className="text-2xl font-black tracking-tight text-white">
                  POCKET
                </h3>
                <p className="text-xs uppercase tracking-widest text-[#F7892A] font-bold">
                  Fashion that fits your pocket.
                </p>
              </div>

              <div className="mt-5 pt-4 border-t border-white/10 w-full flex items-center justify-around text-center text-xs">
                <div>
                  <span className="block font-black text-base text-white">26+</span>
                  <span className="text-[10px] text-slate-400 uppercase">Live Styles</span>
                </div>
                <div className="w-px h-7 bg-white/10" />
                <div>
                  <span className="block font-black text-base text-white">172</span>
                  <span className="text-[10px] text-slate-400 uppercase">Sizes & Colors</span>
                </div>
                <div className="w-px h-7 bg-white/10" />
                <div>
                  <span className="block font-black text-base text-[#F7892A]">4.8 ★</span>
                  <span className="text-[10px] text-slate-400 uppercase">Quality Score</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

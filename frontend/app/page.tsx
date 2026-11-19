import React from 'react';
import Link from 'next/link';
import HeroBanner from '../components/HeroBanner';
import CategoryPills from '../components/CategoryPills';
import ProductCard from '../components/ProductCard';
import { fetchProducts } from '../lib/api';
import { ProductSummary } from '../lib/types';
import { Flame, Sparkles, ArrowRight } from 'lucide-react';

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  // Fetch trending products and general catalog from DRF backend
  const trendingResponse = await fetchProducts({ is_trending: true });
  const allProductsResponse = await fetchProducts({ page: 1 });

  const trendingProducts: ProductSummary[] = trendingResponse.results || [];
  const latestProducts: ProductSummary[] = allProductsResponse.results || [];

  return (
    <div className="space-y-10 pb-16">
      {/* 1. Hero Brand Banner */}
      <HeroBanner />

      {/* 2. Shop By Category (7 core categories) */}
      <CategoryPills />

      {/* 3. Trending Drops Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="flex items-end justify-between mb-6">
          <div>
            <div className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-[#F7892A]">
              <Flame size={15} />
              <span>Hot This Week</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-[#0B162C] tracking-tight">
              Trending Drops
            </h2>
          </div>
          <Link
            href="/category/all"
            className="text-xs sm:text-sm font-bold text-[#0B162C] hover:text-[#F7892A] transition-colors flex items-center space-x-1"
          >
            <span>View All</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        {trendingProducts.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
            {trendingProducts.slice(0, 8).map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-slate-50 rounded-2xl border border-slate-100">
            <p className="text-sm text-slate-500">Loading latest collection from POCKET...</p>
          </div>
        )}
      </section>

      {/* 4. Value Strip / Middle Brand Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-[#0B162C] rounded-2xl p-8 text-white relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 text-center md:text-left z-10">
            <span className="text-xs font-bold uppercase tracking-wider text-[#F7892A]">
              POCKET Brand Guarantee
            </span>
            <h3 className="text-2xl sm:text-3xl font-black tracking-tight">
              Why pay ₹1,499 for a basic tee?
            </h3>
            <p className="text-sm text-slate-300 max-w-xl">
              We cut out distributors, retail store rents, and influencer commissions. You receive heavy 220 GSM combed cotton directly from certified manufacturing hubs.
            </p>
          </div>
          <Link
            href="/category/oversized-t-shirts"
            className="z-10 px-6 py-3 rounded-xl bg-[#F7892A] hover:bg-[#E2761A] text-white font-bold text-sm transition-colors whitespace-nowrap shadow-pocket-orange"
          >
            Shop Direct from ₹399
          </Link>
          <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-[#16284D]/40 to-transparent pointer-events-none" />
        </div>
      </section>

      {/* 5. Complete Wardrobe Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="flex items-end justify-between mb-6">
          <div>
            <div className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-[#0B162C]">
              <Sparkles size={14} className="text-[#F7892A]" />
              <span>Full Collection</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-[#0B162C] tracking-tight">
              New Season Wardrobe
            </h2>
          </div>
          <Link
            href="/category/all"
            className="text-xs sm:text-sm font-bold text-[#0B162C] hover:text-[#F7892A] transition-colors"
          >
            Explore 26+ Designs →
          </Link>
        </div>

        {latestProducts.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
            {latestProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-slate-50 rounded-2xl border border-slate-100">
            <p className="text-sm text-slate-500">All products are updated in real-time from the backend.</p>
          </div>
        )}
      </section>
    </div>
  );
}

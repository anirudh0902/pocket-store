import React from 'react';
import Link from 'next/link';
import { fetchCategoryBySlug, fetchProducts } from '../../../lib/api';
import ProductCard from '../../../components/ProductCard';
import { ProductSummary, Category } from '../../../lib/types';
import { ArrowLeft, Filter, SlidersHorizontal } from 'lucide-react';

interface CategoryPageProps {
  params: {
    slug: string;
  };
  searchParams: {
    ordering?: string;
    search?: string;
    size?: string;
    min_price?: string;
    max_price?: string;
  };
}

export const dynamic = 'force-dynamic';

export default async function CategoryPage({ params, searchParams }: CategoryPageProps) {
  const { slug } = params;
  const isAll = slug === 'all';

  let category: Category | null = null;
  if (!isAll) {
    category = await fetchCategoryBySlug(slug);
  }

  // Fetch products matching category and filters
  const productsResponse = await fetchProducts({
    category: isAll ? undefined : slug,
    search: searchParams.search,
    ordering: searchParams.ordering || '-id',
    size: searchParams.size,
    min_price: searchParams.min_price ? parseFloat(searchParams.min_price) : undefined,
    max_price: searchParams.max_price ? parseFloat(searchParams.max_price) : undefined,
  });

  const products: ProductSummary[] = productsResponse.results || [];
  const title = isAll ? 'All Men’s Collection' : category?.name || slug.replace(/-/g, ' ').toUpperCase();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="flex items-center space-x-2 text-xs text-slate-500 mb-6">
        <Link href="/" className="hover:text-[#F7892A] transition-colors">Home</Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">{title}</span>
      </nav>

      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-200 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-[#0B162C] capitalize">
            {title}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Showing {products.length} {products.length === 1 ? 'item' : 'items'} • Direct-to-Consumer Pricing
          </p>
        </div>

        {/* Sort Controls */}
        <div className="flex items-center space-x-3 text-xs">
          <span className="text-slate-500 font-medium hidden sm:inline">Sort by:</span>
          <div className="flex items-center space-x-2">
            <Link
              href={`/category/${slug}?ordering=-id`}
              className={`px-3 py-1.5 rounded-full border transition-colors ${
                !searchParams.ordering || searchParams.ordering === '-id'
                  ? 'bg-[#0B162C] text-white border-[#0B162C]'
                  : 'bg-white text-slate-700 border-slate-300 hover:border-slate-400'
              }`}
            >
              Latest
            </Link>
            <Link
              href={`/category/${slug}?ordering=price_asc`}
              className={`px-3 py-1.5 rounded-full border transition-colors ${
                searchParams.ordering === 'price_asc'
                  ? 'bg-[#0B162C] text-white border-[#0B162C]'
                  : 'bg-white text-slate-700 border-slate-300 hover:border-slate-400'
              }`}
            >
              Price: Low to High
            </Link>
            <Link
              href={`/category/${slug}?ordering=price_desc`}
              className={`px-3 py-1.5 rounded-full border transition-colors ${
                searchParams.ordering === 'price_desc'
                  ? 'bg-[#0B162C] text-white border-[#0B162C]'
                  : 'bg-white text-slate-700 border-slate-300 hover:border-slate-400'
              }`}
            >
              Price: High to Low
            </Link>
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="pt-8">
        {products.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-slate-50 rounded-2xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-800">No products found</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              We couldn’t find any products in this category right now. Check back soon or explore our complete catalog.
            </p>
            <Link
              href="/category/all"
              className="mt-5 inline-block px-5 py-2.5 bg-[#0B162C] text-white text-xs font-bold rounded-lg hover:bg-[#16284D] transition-colors"
            >
              Browse All Products
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ProductSummary } from '../lib/types';
import { Star, ShoppingBag } from 'lucide-react';
import { useCart } from '../lib/cart-context';

interface ProductCardProps {
  product: ProductSummary;
}

export default function ProductCard({ product }: ProductCardProps) {
  const { addItem, isLoading } = useCart();

  const handleQuickAdd = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    // Quick add adds the base product
    await addItem(product.id, null, 1);
  };

  const imageUrl = product.primary_image_url || '/pocket_logo.jpg';

  return (
    <div className="group bg-white rounded-xl overflow-hidden border border-slate-200/80 hover:border-slate-300 hover:shadow-lg transition-all duration-300 flex flex-col h-full">
      <Link href={`/product/${product.slug}`} className="block relative aspect-[3/4] w-full bg-slate-100 overflow-hidden">
        <Image
          src={imageUrl}
          alt={product.name}
          fill
          sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
          className="object-cover object-top group-hover:scale-105 transition-transform duration-500"
        />

        {/* Badges Overlay */}
        <div className="absolute top-2.5 left-2.5 flex flex-col gap-1.5 z-10">
          {product.has_discount && product.discount_percentage > 0 && (
            <span className="bg-[#F7892A] text-white text-[10px] font-extrabold px-2 py-0.5 rounded shadow-sm">
              {product.discount_percentage}% OFF
            </span>
          )}
          {product.is_bestseller && (
            <span className="bg-[#0B162C] text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm">
              BESTSELLER
            </span>
          )}
        </div>

        {/* Rating Badge */}
        {product.average_rating > 0 && (
          <div className="absolute bottom-2.5 left-2.5 bg-white/95 backdrop-blur-sm px-2 py-0.5 rounded flex items-center space-x-1 text-[11px] font-bold text-slate-800 shadow-sm">
            <span>{product.average_rating.toFixed(1)}</span>
            <Star size={11} className="fill-[#F7892A] text-[#F7892A]" />
            {product.reviews_count > 0 && (
              <span className="text-slate-400 font-normal">({product.reviews_count})</span>
            )}
          </div>
        )}
      </Link>

      {/* Product Info */}
      <div className="p-3.5 flex flex-col flex-1 justify-between">
        <div>
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wide">
            {product.category_name}
          </span>
          <Link href={`/product/${product.slug}`}>
            <h3 className="text-sm font-semibold text-[#0B162C] line-clamp-2 mt-0.5 hover:text-[#F7892A] transition-colors leading-snug">
              {product.name}
            </h3>
          </Link>
        </div>

        <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
          <div className="flex items-baseline space-x-2">
            <span className="text-base font-extrabold text-[#0B162C]">
              ₹{Math.round(parseFloat(product.selling_price))}
            </span>
            {parseFloat(product.original_price) > parseFloat(product.selling_price) && (
              <span className="text-xs text-slate-400 line-through">
                ₹{Math.round(parseFloat(product.original_price))}
              </span>
            )}
          </div>

          <button
            onClick={handleQuickAdd}
            disabled={!product.is_in_stock || isLoading}
            className="p-2 rounded-lg bg-slate-100 text-slate-700 hover:bg-[#0B162C] hover:text-white transition-colors"
            title="Add to Bag"
            aria-label="Add to Bag"
          >
            <ShoppingBag size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

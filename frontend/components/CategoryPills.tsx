import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

interface CategoryItem {
  name: string;
  slug: string;
  tag: string;
  image: string;
}

const FEATURED_CATEGORIES: CategoryItem[] = [
  {
    name: 'Oversized T-shirts',
    slug: 'oversized-t-shirts',
    tag: 'Streetwear Drop',
    image: '/categories/oversized-t-shirts.jpg',
  },
  {
    name: 'Graphic T-shirts',
    slug: 'graphic-t-shirts',
    tag: 'Typography & Art',
    image: '/categories/graphic-t-shirts.jpg',
  },
  {
    name: 'Basic T-shirts',
    slug: 'basic-t-shirts',
    tag: '220 GSM Combed Cotton',
    image: '/categories/basic-t-shirts.jpg',
  },
  {
    name: 'Polo T-shirts',
    slug: 'polo-t-shirts',
    tag: 'Honeycomb Knit',
    image: '/categories/polo-t-shirts.jpg',
  },
  {
    name: 'Casual Shirts',
    slug: 'casual-shirts',
    tag: 'Oxford & Linen',
    image: '/categories/casual-shirts.jpg',
  },
  {
    name: 'Joggers',
    slug: 'joggers',
    tag: '4-Way Stretch Lycra',
    image: '/categories/joggers.jpg',
  },
  {
    name: 'Cargo Pants',
    slug: 'cargo-pants',
    tag: '6-Pocket Utility Twill',
    image: '/categories/cargo-pants.jpg',
  },
];

export default function CategoryPills() {
  return (
    <section className="py-10 bg-slate-50 border-y border-slate-200/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between mb-6">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-[#F7892A]">
              Curated Wardrobe
            </span>
            <h2 className="text-2xl font-black text-[#0B162C] tracking-tight">
              Shop by Category
            </h2>
          </div>
          <Link
            href="/category/all"
            className="text-xs font-bold text-[#0B162C] hover:text-[#F7892A] transition-colors"
          >
            View All ({FEATURED_CATEGORIES.length}) →
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 sm:gap-4">
          {FEATURED_CATEGORIES.map((cat) => (
            <Link
              key={cat.slug}
              href={`/category/${cat.slug}`}
              className="group bg-white rounded-xl p-3 border border-slate-200/70 hover:border-[#F7892A] hover:shadow-md transition-all duration-300 flex flex-col items-center text-center"
            >
              <div className="relative w-16 h-16 sm:w-20 sm:h-20 rounded-full overflow-hidden bg-slate-100 mb-2.5 border-2 border-slate-100 group-hover:border-[#F7892A] transition-colors">
                <Image
                  src={cat.image}
                  alt={cat.name}
                  fill
                  sizes="80px"
                  className="object-cover group-hover:scale-110 transition-transform duration-300"
                />
              </div>
              <h3 className="text-xs font-bold text-[#0B162C] group-hover:text-[#F7892A] transition-colors">
                {cat.name}
              </h3>
              <span className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">
                {cat.tag}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image_url?: string | null;
  products_count?: number;
}

export interface ProductVariant {
  id: number;
  size: string;
  color: string;
  color_code?: string;
  stock_quantity: number;
  is_in_stock: boolean;
}

export interface ProductImage {
  id: number;
  image_url: string;
  alt_text?: string;
  is_primary: boolean;
  display_order: number;
}

export interface ProductReview {
  id: number;
  user_name: string;
  rating: number;
  title: string;
  comment: string;
  created_at: string;
}

export interface ProductSummary {
  id: number;
  name: string;
  slug: string;
  category_name: string;
  category_slug: string;
  selling_price: string;
  original_price: string;
  has_discount: boolean;
  discount_percentage: number;
  primary_image_url: string | null;
  is_in_stock: boolean;
  is_trending: boolean;
  is_bestseller: boolean;
  average_rating: number;
  reviews_count: number;
}

export interface ProductDetail {
  id: number;
  name: string;
  slug: string;
  category: Category;
  description: string;
  specifications: string;
  selling_price: string;
  original_price: string;
  has_discount: boolean;
  discount_percentage: number;
  is_in_stock: boolean;
  stock_quantity: number;
  images: ProductImage[];
  variants: ProductVariant[];
  reviews: ProductReview[];
  is_trending: boolean;
  is_bestseller: boolean;
  average_rating: number;
  reviews_count: number;
  created_at: string;
}

export interface CartItem {
  id: number;
  product: ProductSummary;
  variant: ProductVariant | null;
  quantity: number;
  total_price: string;
  created_at: string;
}

export interface Cart {
  id: number;
  total_items: number;
  subtotal: string;
  shipping_fee: string;
  free_shipping_threshold: string;
  free_shipping_remaining: string;
  qualifies_for_free_shipping: boolean;
  total_amount: string;
  items: CartItem[];
  updated_at: string;
}

export interface OrderItem {
  id: number;
  product_name: string;
  variant_details: string;
  unit_price: string;
  quantity: number;
  total_price: string;
}

export interface OrderStatusHistory {
  status: string;
  comment: string;
  created_at: string;
}

export interface OrderDetail {
  id: number;
  order_number: string;
  status: string;
  status_display: string;
  payment_status: string;
  payment_status_display: string;
  subtotal: string;
  shipping_fee: string;
  total_amount: string;
  shipping_address_snapshot: Record<string, string>;
  customer_notes?: string;
  items: OrderItem[];
  status_history: OrderStatusHistory[];
  created_at: string;
  updated_at: string;
}

export interface UPIDetails {
  order_number: string;
  amount: string;
  upi_id: string;
  account_display_name: string;
  upi_intent_url: string;
  payment_instructions: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
}

export interface CustomerAddress {
  id: number;
  full_name: string;
  phone: string;
  street_address: string;
  apartment_suite?: string;
  city: string;
  state: string;
  postal_code: string;
  landmark?: string;
  is_default: boolean;
}

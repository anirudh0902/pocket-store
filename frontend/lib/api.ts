import {
  Category,
  ProductSummary,
  ProductDetail,
  Cart,
  OrderDetail,
  UPIDetails,
  PaginatedResponse,
  UserProfile,
  CustomerAddress,
} from './types';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

// Client-side helper to get or create guest cart session token
export function getCartSessionToken(): string {
  if (typeof window === 'undefined') return '';
  let token = localStorage.getItem('pocket_cart_session');
  if (!token) {
    token = 'guest_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
    localStorage.setItem('pocket_cart_session', token);
  }
  return token;
}

// Client-side helper for auth token
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('pocket_auth_token');
}

// Universal fetch wrapper with headers
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  const headers = new Headers(options.headers || {});

  headers.set('Content-Type', 'application/json');
  headers.set('Accept', 'application/json');

  if (typeof window !== 'undefined') {
    const sessionToken = getCartSessionToken();
    if (sessionToken) {
      headers.set('X-Cart-Session', sessionToken);
    }
    const authToken = getAuthToken();
    if (authToken) {
      headers.set('Authorization', `Bearer ${authToken}`);
    }
  }

  const fetchOptions: RequestInit = {
    ...options,
    headers,
  };
  if (options.cache) {
    fetchOptions.cache = options.cache;
  }

  const response = await fetch(url, fetchOptions);

  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      errorDetail = `Status ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

// ----------------------------------------------------
// CATALOG APIS
// ----------------------------------------------------

export async function fetchCategories(): Promise<Category[]> {
  try {
    return await apiFetch<Category[]>('/categories/');
  } catch (err) {
    console.error('Failed to fetch categories:', err);
    return [];
  }
}

export async function fetchCategoryBySlug(slug: string): Promise<Category | null> {
  try {
    return await apiFetch<Category>(`/categories/${slug}/`);
  } catch (err) {
    console.error(`Failed to fetch category ${slug}:`, err);
    return null;
  }
}

export interface ProductFilterParams {
  category?: string;
  search?: string;
  ordering?: string;
  min_price?: number;
  max_price?: number;
  size?: string;
  is_trending?: boolean;
  is_bestseller?: boolean;
  page?: number;
}

export async function fetchProducts(
  params: ProductFilterParams = {}
): Promise<PaginatedResponse<ProductSummary>> {
  const query = new URLSearchParams();
  if (params.category) query.set('category', params.category);
  if (params.search) query.set('search', params.search);
  if (params.ordering) query.set('ordering', params.ordering);
  if (params.min_price) query.set('min_price', params.min_price.toString());
  if (params.max_price) query.set('max_price', params.max_price.toString());
  if (params.size) query.set('size', params.size);
  if (params.is_trending) query.set('is_trending', 'true');
  if (params.is_bestseller) query.set('is_bestseller', 'true');
  if (params.page) query.set('page', params.page.toString());

  const qs = query.toString();
  try {
    return await apiFetch<PaginatedResponse<ProductSummary>>(`/products/${qs ? `?${qs}` : ''}`);
  } catch (err) {
    console.error('Failed to fetch products:', err);
    return { count: 0, next: null, previous: null, results: [] };
  }
}

export async function fetchProductBySlug(slug: string): Promise<ProductDetail | null> {
  try {
    return await apiFetch<ProductDetail>(`/products/${slug}/`);
  } catch (err) {
    console.error(`Failed to fetch product ${slug}:`, err);
    return null;
  }
}

// ----------------------------------------------------
// CART APIS
// ----------------------------------------------------

export async function fetchCart(): Promise<Cart | null> {
  try {
    return await apiFetch<Cart>('/cart/');
  } catch (err) {
    console.error('Failed to fetch cart:', err);
    return null;
  }
}

export async function addToCart(
  productId: number,
  variantId: number | null,
  quantity = 1
): Promise<Cart> {
  return await apiFetch<Cart>('/cart/add/', {
    method: 'POST',
    body: JSON.stringify({
      product_id: productId,
      variant_id: variantId,
      quantity,
    }),
  });
}

export async function updateCartItem(
  itemId: number,
  quantity: number
): Promise<Cart> {
  return await apiFetch<Cart>(`/cart/update/${itemId}/`, {
    method: 'POST',
    body: JSON.stringify({ quantity }),
  });
}

export async function removeCartItem(itemId: number): Promise<Cart> {
  return await apiFetch<Cart>(`/cart/remove/${itemId}/`, {
    method: 'POST',
  });
}

export async function clearCart(): Promise<{ message: string }> {
  return await apiFetch<{ message: string }>('/cart/clear/', {
    method: 'POST',
  });
}

// ----------------------------------------------------
// CHECKOUT & ORDERS
// ----------------------------------------------------

export interface CheckoutPayload {
  full_name: string;
  phone: string;
  street_address: string;
  apartment_suite?: string;
  city: string;
  state: string;
  postal_code: string;
  landmark?: string;
  customer_notes?: string;
}

export interface CheckoutResult {
  message: string;
  order: OrderDetail;
  payment: UPIDetails;
}

export async function submitCheckout(payload: CheckoutPayload): Promise<CheckoutResult> {
  return await apiFetch<CheckoutResult>('/orders/checkout/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchOrderDetail(orderNumber: string): Promise<OrderDetail> {
  return await apiFetch<OrderDetail>(`/orders/${orderNumber}/`);
}

export async function trackOrder(orderNumber: string, phone: string): Promise<OrderDetail> {
  return await apiFetch<OrderDetail>(
    `/orders/track/?order_number=${encodeURIComponent(orderNumber)}&phone=${encodeURIComponent(phone)}`
  );
}

// ----------------------------------------------------
// UPI & PAYMENT VERIFICATION
// ----------------------------------------------------

export async function fetchUPIDetails(orderNumber: string): Promise<UPIDetails> {
  return await apiFetch<UPIDetails>(`/payments/upi-details/?order_number=${encodeURIComponent(orderNumber)}`);
}

export interface SubmitUTRPayload {
  order_number: string;
  utr_number: string;
  payer_name: string;
  payer_phone: string;
}

export async function submitUTR(payload: SubmitUTRPayload): Promise<{
  message: string;
  order_number: string;
  payment_status: string;
  verification_mode: string;
}> {
  return await apiFetch('/payments/submit-utr/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

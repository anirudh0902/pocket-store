'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { Cart } from './types';
import { fetchCart, addToCart as apiAddToCart, updateCartItem as apiUpdateCartItem, removeCartItem as apiRemoveCartItem, clearCart as apiClearCart } from './api';

interface CartContextType {
  cart: Cart | null;
  itemCount: number;
  isLoading: boolean;
  isCartOpen: boolean;
  setIsCartOpen: (open: boolean) => void;
  refreshCart: () => Promise<void>;
  addItem: (productId: number, variantId: number | null, quantity?: number) => Promise<boolean>;
  updateItem: (itemId: number, quantity: number) => Promise<boolean>;
  removeItem: (itemId: number) => Promise<boolean>;
  emptyCart: () => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isCartOpen, setIsCartOpen] = useState<boolean>(false);

  const refreshCart = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await fetchCart();
      setCart(data);
    } catch (err) {
      console.error('Error loading cart in context:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  const addItem = async (productId: number, variantId: number | null, quantity = 1): Promise<boolean> => {
    try {
      setIsLoading(true);
      const updatedCart = await apiAddToCart(productId, variantId, quantity);
      setCart(updatedCart);
      setIsCartOpen(true);
      return true;
    } catch (err: any) {
      console.error('Add to cart failed:', err);
      alert(err.message || 'Could not add product to cart');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const updateItem = async (itemId: number, quantity: number): Promise<boolean> => {
    try {
      setIsLoading(true);
      const updatedCart = await apiUpdateCartItem(itemId, quantity);
      setCart(updatedCart);
      return true;
    } catch (err: any) {
      console.error('Update cart item failed:', err);
      alert(err.message || 'Could not update quantity');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const removeItem = async (itemId: number): Promise<boolean> => {
    try {
      setIsLoading(true);
      const updatedCart = await apiRemoveCartItem(itemId);
      setCart(updatedCart);
      return true;
    } catch (err: any) {
      console.error('Remove cart item failed:', err);
      alert(err.message || 'Could not remove item');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const emptyCart = async (): Promise<void> => {
    try {
      setIsLoading(true);
      await apiClearCart();
      setCart(null);
    } catch (err: any) {
      console.error('Clear cart failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const itemCount = cart?.total_items || 0;

  return (
    <CartContext.Provider
      value={{
        cart,
        itemCount,
        isLoading,
        isCartOpen,
        setIsCartOpen,
        refreshCart,
        addItem,
        updateItem,
        removeItem,
        emptyCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}

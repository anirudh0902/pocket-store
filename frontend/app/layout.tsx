import type { Metadata } from 'next';
import './globals.css';
import { CartProvider } from '../lib/cart-context';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export const metadata: Metadata = {
  title: 'POCKET | Fashion that fits your pocket',
  description:
    'Official POCKET online store. Premium 220 GSM combed cotton oversized tees, graphic tees, structured polos, joggers, and utility cargo pants at honest direct prices.',
  icons: {
    icon: '/pocket_logo.jpg',
    apple: '/pocket_logo.jpg',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-white text-[#0B162C]">
        <CartProvider>
          <Navbar />
          <main className="flex-1">{children}</main>
          <Footer />
        </CartProvider>
      </body>
    </html>
  );
}

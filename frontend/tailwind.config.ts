import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        pocket: {
          navy: '#0B162C',
          'navy-light': '#16284D',
          'navy-dark': '#060D1B',
          orange: '#F7892A',
          'orange-hover': '#E2761A',
          'orange-light': '#FFF5EB',
          gray: '#F8FAFC',
          card: '#FFFFFF',
          border: '#E2E8F0',
          text: '#0B162C',
          muted: '#64748B',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'pocket': '0 4px 20px -2px rgba(11, 22, 44, 0.08)',
        'pocket-lg': '0 10px 25px -3px rgba(11, 22, 44, 0.12)',
        'pocket-orange': '0 4px 14px 0 rgba(247, 137, 42, 0.39)',
      },
    },
  },
  plugins: [],
};

export default config;

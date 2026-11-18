# POCKET E-Commerce Platform

> **Fashion that fits your pocket.**

Official production-ready Django e-commerce web platform for **POCKET**, designed for high quality, accessible Indian retail fashion with manual UPI payment verification, supplier procurement management, real-time logistics tracking, and net profit analytics.

---

## 1. Brand Identity & Design System

- **Brand Name:** POCKET
- **Official Tagline:** *Fashion that fits your pocket.*
- **Official Logo:** Preserved intact at `static/images/pocket_logo.jpg` with exact proportions and appearance across the storefront header, footer, favicon, checkout, order confirmations, and the custom Admin Dashboard.
- **Color Palette:**
  - **Primary Brand Color:** Dark Navy (`#0B162C` / `#162238`) matching the official logo background.
  - **Accent Brand Color:** Warm Orange (`#F7892A` / `#EA580C`) matching the official shopping bag logo icon.
  - **Backgrounds:** Clean White (`#FFFFFF`) with slate neutrals (`#F8FAFC`, `#F1F5F9`).

---

## 2. Technology Stack

- **Backend:** Python 3.12, Django 6.1 (Modular Architecture, Django ORM, Messages Framework, Auth System)
- **Frontend:** HTML5, Tailwind CSS, Alpine.js, SVG Iconography, Responsive Mobile Drawers
- **Database:** SQLite (local dev), PostgreSQL-ready architecture via `DATABASE_URL`
- **Image Processing:** Pillow 13.0
- **Configuration:** `python-dotenv` (`.env` environment variable isolation)

---

## 3. Project Architecture

```
d:\POCKET\
├── pocket_config/          # Core Django settings, URL router, WSGI/ASGI
├── core/                   # Homepage, About, Contact, Policies, Site Context Processor
├── accounts/               # Custom User, CustomerAddress, Auth, Profile, My Orders
├── products/               # Category, Product, ProductImage, ProductVariant, Reviews
├── orders/                 # Cart, CartItem, Wishlist, Order, OrderItem, ShippingDetails
├── payments/               # SiteConfiguration, Manual UPI Payment verification
├── admin_dashboard/        # Custom Executive Dashboard, Suppliers, P&L Reports
├── notifications/          # Customer in-app order updates & notification desk
├── static/
│   ├── images/             # pocket_logo.jpg (Official logo)
│   ├── css/
│   └── js/
├── media/                  # Uploaded products, UPI QR codes, receipts
├── templates/              # Reusable Django template component hierarchy
├── requirements.txt        # Pinned dependencies
├── .env.example            # Environment variables template
└── manage.py
```

---

## 4. Business Workflow & Manual UPI Model

POCKET operates a retail & supplier-based fulfillment model:

1. **Product Curation:** Admin lists fashion items with customer selling prices and internal supplier purchase costs (strictly hidden from customers).
2. **Browsing & Cart:** Customers browse responsive grids with genuine filters and add items with size/color variants to their server-validated cart.
3. **Checkout:** Customer selects or adds a delivery address. Cash on Delivery is strictly prohibited (*"Cash on Delivery is not available. Please pay online to confirm your order."*).
4. **Order Creation:** Generates a unique order number (`PKT-YYYYMMDD-XXXX`) and freezes price/supplier-cost snapshots.
5. **Direct UPI Payment:** Website presents the configured UPI QR code and deep-link (`upi://pay?pa=...`).
6. **UTR Submission:** Customer makes payment in GPay/PhonePe/Paytm and submits the 12-digit bank UTR reference number. Order moves to `Payment Verification`.
7. **Admin Bank Audit:** Authorized admin verifies transaction in the bank statement, then clicks **Approve** (transitions order to `Payment Verified`) or **Reject**. Duplicate verified UTRs are rejected automatically.
8. **Supplier Procurement:** Admin places order with supplier (e.g. Meesho/Flipkart seller or direct manufacturer). *Rule: Supplier purchasing is blocked until payment is verified.*
9. **Logistics & Tracking:** Admin inputs courier partner (Delhivery, BlueDart, DTDC, XpressBees) and tracking AWB. Customer receives tracking update in real-time.
10. **Net Profit Reporting:** System computes exact net profit:
    $$\text{Estimated Profit} = \text{Selling Price} - \text{Supplier Cost} - \text{Shipping} - \text{Packaging} - \text{Payment Fees} - \text{Other Expenses}$$

---

## 5. Quickstart & Local Setup

### Step 1: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run Database Migrations
```powershell
python manage.py migrate
```

### Step 4: Seed Initial Data (Admin, Config, Categories, Products)
```powershell
python manage.py seed_pocket_data
```
Default Credentials:
- **Admin Portal URL:** `http://127.0.0.1:8000/admin-portal/`
- **Username:** `admin`
- **Password:** `PocketAdmin2026!`

### Step 5: Start Development Server
```powershell
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your web browser.

---

## 6. Running the Automated Test Suite

POCKET includes 16 tests covering customer authentication, cart and shipping calculation, order creation, UPI payment submission, duplicate UTR prevention, order isolation, supplier information privacy, and net profit calculations:

```powershell
python manage.py test
```

---

## 7. Production Checklist

- Set `DEBUG=False` in `.env`.
- Generate a unique `DJANGO_SECRET_KEY`.
- Configure `ALLOWED_HOSTS` to your registered production domain.
- Set up PostgreSQL and configure `DATABASE_URL`.
- Run `python manage.py collectstatic --noinput`.
- Serve with Gunicorn or Uvicorn behind Nginx with SSL (HTTPS).

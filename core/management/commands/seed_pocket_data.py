import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from accounts.models import User
from payments.models import SiteConfiguration
from products.models import Category, Product, ProductVariant, ProductImage
from admin_dashboard.models import Supplier


class Command(BaseCommand):
    help = "Seeds initial database for POCKET: admin user, site config, categories, suppliers, and realistic products."

    def handle(self, *args, **options):
        self.stdout.write("Seeding POCKET data...")

        # 1. Admin Superuser
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@pocketfashion.in',
                'first_name': 'Anirudh',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
                'is_pocket_admin': True,
            }
        )
        if created:
            admin_user.set_password('PocketAdmin2026!')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / PocketAdmin2026!"))
        else:
            self.stdout.write("Admin user already exists.")

        # 2. Site Configuration
        config = SiteConfiguration.get_solo()
        config.site_name = "POCKET"
        config.tagline = "Fashion that fits your pocket."
        config.upi_id = "pocketfashion@upi"
        config.account_display_name = "POCKET FASHION STORE"
        config.free_shipping_threshold = Decimal('499.00')
        config.standard_shipping_charge = Decimal('49.00')
        config.support_phone = "+91 98765 43210"
        config.support_email = "support@pocketfashion.in"
        config.payment_instructions = (
            "1. Scan the QR code using Google Pay, PhonePe, Paytm, BHIM, or any UPI app.\n"
            "2. Pay the exact order amount.\n"
            "3. Copy the 12-digit UTR / Bank Reference Number from your payment app.\n"
            "4. Enter the UTR number below and click 'Submit Payment'.\n"
            "5. Our team verifies the transaction with our bank account before confirming your order."
        )
        config.save()
        self.stdout.write(self.style.SUCCESS("Updated SiteConfiguration."))

        # 3. Suppliers (Internal)
        suppliers_list = [
            ("Radha Krishna Tex (Surat Hub)", "MANUFACTURER", "Ramesh Bhai", "+91 98251 12345", "rktex.surat@gmail.com", "https://surattextilemarket.com/rktex", "Specialist in rayon kurtis and cotton sarees. Reliable 48h dispatch."),
            ("TrendHub Apparel (Tirupur)", "MEESHO", "Senthil Kumar", "+91 94432 98765", "trendhub.tirupur@reseller.in", "https://meesho.com/supplier/trendhub-apparel", "100% bio-washed combed cotton t-shirts and oversized tees. High-volume Tirupur knitwear supplier."),
            ("UrbanStride Footwear (Agra)", "LOCAL_DISTRIBUTOR", "Mohit Sharma", "+91 97190 54321", "urbanstride.agra@gmail.com", "", "Breathable mesh sneakers and everyday casual loafers."),
            ("Classic Knitwear Works (Tirupur Cluster)", "MANUFACTURER", "V. Murugan", "+91 94421 87654", "classicknitwear.tirupur@gmail.com", "https://www.indiamart.com/classicknitwear-tirupur/", "IndiaMART verified manufacturer of 220-240 GSM French Terry oversized tees and 100% cotton pique polo t-shirts."),
            ("Shopsy Retail Hub (Surat & Tirupur)", "FLIPKART", "Rajesh Patel", "+91 98250 44321", "shopsy.resellerhub@surattextiles.in", "https://www.flipkart.com/shopsy-seller-hub", "Shopsy/Flipkart reseller partner for cotton casual shirts and budget lycra joggers."),
            ("Vardhman Hosiery Mills (Ludhiana)", "MANUFACTURER", "Harpreet Singh", "+91 98140 22334", "vardhmanhosiery.ldh@gmail.com", "https://www.indiamart.com/vardhmanhosiery-ldh/", "Ludhiana hosiery cluster. IndiaMART verified supplier of 4-way stretch lycra gym joggers."),
            ("Apex Garment Mfg & Twill Works (Ahmedabad)", "MANUFACTURER", "Chetan Shah", "+91 98790 65432", "apexgarments.ahd@yahoo.com", "https://www.indiamart.com/apexgarments-ahd/", "Ahmedabad textile hub. IndiaMART verified supplier of 6-pocket tactical cargo pants."),
            ("Surat Weaves & Cottons (Surat Textile Market)", "MANUFACTURER", "Dharmendra Chawla", "+91 98241 78901", "suratweaves.mill@gmail.com", "https://www.indiamart.com/suratweaves-mill/", "Surat textile hub. IndiaMART verified supplier of 100% pure cotton Oxford shirts and cotton-linen checks."),
            ("UrbanResell Fashion Network (Delhi Hub)", "OTHER", "Amit Verma", "+91 98110 99887", "urbanresell.delhi@gmail.com", "https://meesho.com/supplier/urbanresell-delhi", "Gandhi Nagar wholesale apparel hub, Delhi. Multi-channel marketplace reseller supplier."),
        ]
        supplier_objs = {}
        for s_name, s_plat, s_contact, s_phone, s_email, s_url, s_notes in suppliers_list:
            sup, _ = Supplier.objects.get_or_create(
                name=s_name,
                defaults={
                    'platform': s_plat,
                    'contact_person': s_contact,
                    'phone': s_phone,
                    'email': s_email,
                    'website_or_store_url': s_url,
                    'internal_notes': s_notes
                }
            )
            supplier_objs[s_name] = sup
        s1 = supplier_objs["Radha Krishna Tex (Surat Hub)"]
        s2 = supplier_objs["TrendHub Apparel (Tirupur)"]
        s3 = supplier_objs["UrbanStride Footwear (Agra)"]
        self.stdout.write(self.style.SUCCESS("Suppliers initialized."))

        # 4. Categories (including specific clothing departments)
        categories_data = [
            ("Oversized T-shirts", "Relaxed, dropped-shoulder heavyweight oversized tees designed for effortless streetwear style.", 1, "categories/oversized-t-shirts.jpg"),
            ("Graphic T-shirts", "Bold graphic prints, typography, and vibrant artistic designs on premium breathable cotton.", 2, "categories/graphic-t-shirts.jpg"),
            ("Basic T-shirts", "Everyday solid essentials in classic crew and v-neck cuts crafted from ultra-soft combed cotton.", 3, "categories/basic-t-shirts.jpg"),
            ("Polo T-shirts", "Smart collared polos with ribbed cuffs and subtle detailing, perfect for casual and semi-formal wear.", 4, "categories/polo-t-shirts.jpg"),
            ("Casual Shirts", "Classic Oxford, linen blend, checks, and relaxed button-down shirts tailored for versatile styling.", 5, "categories/casual-shirts.jpg"),
            ("Joggers", "Ultra-comfortable athletic and street joggers with elastic drawstrings and tailored tapered ankles.", 6, "categories/joggers.jpg"),
            ("Cargo Pants", "Rugged multi-pocket utility cargo trousers built with stretch twill and reinforced stitching.", 7, "categories/cargo-pants.jpg"),
            ("Men's Fashion", "Trendy shirts, casual t-shirts, jackets, and formal wear.", 8, "categories/mens-fashion.jpg"),
            ("Women's Ethnic & Western", "Graceful kurtas, stylish tops, dresses, and co-ord sets.", 9, "categories/womens-ethnic-western.jpg"),
            ("Trendy T-Shirts & Tops", "Oversized graphic tees, solid polo shirts, and casual tops.", 10, "categories/trendy-t-shirts-tops.jpg"),
            ("Bottoms & Denims", "Stretchable denim jeans, cargo trousers, and comfortable joggers.", 11, "categories/bottoms-denims.jpg"),
            ("Footwear & Sneakers", "Comfortable everyday sneakers, loafers, and walking shoes.", 12, "categories/footwear-sneakers.jpg"),
            ("Accessories & Bags", "Backpacks, belts, wallets, and daily fashion accessories.", 13, "categories/accessories-bags.jpg"),
        ]
        cat_objs = {}
        for item in categories_data:
            name, desc, order = item[0], item[1], item[2]
            img = item[3] if len(item) > 3 else ""
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'display_order': order, 'is_active': True, 'image': img}
            )
            if not created:
                cat.display_order = order
                cat.description = desc
                if img and not cat.image:
                    cat.image = img
                cat.save()
            cat_objs[name] = cat
        self.stdout.write(self.style.SUCCESS("Categories initialized."))

        # 5. Products
        products_data = [
            {
                'name': 'POCKET Classic Heavyweight 220 GSM Oversized Cotton T-Shirt',
                'category': cat_objs["Trendy T-Shirts & Tops"],
                'description': 'Elevate your daily streetwear with the POCKET Classic Heavyweight Oversized Tee. Crafted from 100% combed bio-washed cotton (220 GSM), it provides a relaxed boxy fit, dropped shoulders, and durable ribbed collar that holds shape wash after wash.',
                'specifications': 'Fabric: 100% Combed Cotton | GSM: 220 GSM Heavyweight | Fit: Relaxed Oversized Fit | Neck: Ribbed Crew Neck | Wash Care: Machine wash cold, tumble dry low',
                'selling_price': Decimal('499.00'),
                'original_price': Decimal('899.00'),
                'source_cost': Decimal('220.00'),
                'stock_quantity': 45,
                'supplier': s2,
                'is_bestseller': True,
                'is_trending': True,
                'is_featured': True,
                'variants': [
                    {'size': 'S', 'color': 'Navy Blue', 'color_code': '#0B162C', 'stock': 10},
                    {'size': 'M', 'color': 'Navy Blue', 'color_code': '#0B162C', 'stock': 15},
                    {'size': 'L', 'color': 'Navy Blue', 'color_code': '#0B162C', 'stock': 12},
                    {'size': 'XL', 'color': 'Navy Blue', 'color_code': '#0B162C', 'stock': 8},
                ]
            },
            {
                'name': 'POCKET Pure Cotton Embroidered Straight Kurta with Dupatta Set',
                'category': cat_objs["Women's Ethnic & Western"],
                'description': 'A graceful ethnic ensemble designed for both festive occasions and everyday elegance. Made with breathable premium cotton featuring delicate thread embroidery on the neckline and sleeves, accompanied by a coordinating soft dupatta.',
                'specifications': 'Kurta Fabric: 100% Cotton | Dupatta Fabric: Mulmul Cotton | Pattern: Embroidered | Length: Calf Length | Sleeve: 3/4th Sleeve',
                'selling_price': Decimal('799.00'),
                'original_price': Decimal('1499.00'),
                'source_cost': Decimal('380.00'),
                'stock_quantity': 30,
                'supplier': s1,
                'is_bestseller': True,
                'is_trending': True,
                'is_featured': True,
                'variants': [
                    {'size': 'M', 'color': 'Rust Orange', 'color_code': '#F7892A', 'stock': 10},
                    {'size': 'L', 'color': 'Rust Orange', 'color_code': '#F7892A', 'stock': 12},
                    {'size': 'XL', 'color': 'Rust Orange', 'color_code': '#F7892A', 'stock': 8},
                ]
            },
            {
                'name': 'POCKET Slim Fit Oxford Casual Shirt with Pocket Monogram',
                'category': cat_objs["Men's Fashion"],
                'description': 'The quintessential modern button-down shirt. Woven from breathable Oxford cotton with a subtle texture, tailored in a flattering slim silhouette suitable for work, weekends, and evening get-togethers.',
                'specifications': 'Fabric: 100% Oxford Cotton | Collar: Button-Down Collar | Fit: Slim Fit | Pattern: Solid | Hem: Curved Hem',
                'selling_price': Decimal('649.00'),
                'original_price': Decimal('1199.00'),
                'source_cost': Decimal('310.00'),
                'stock_quantity': 35,
                'supplier': s2,
                'is_bestseller': False,
                'is_trending': True,
                'is_featured': True,
                'variants': [
                    {'size': '38', 'color': 'Sky Blue', 'color_code': '#93C5FD', 'stock': 8},
                    {'size': '40', 'color': 'Sky Blue', 'color_code': '#93C5FD', 'stock': 12},
                    {'size': '42', 'color': 'Sky Blue', 'color_code': '#93C5FD', 'stock': 10},
                    {'size': '44', 'color': 'Sky Blue', 'color_code': '#93C5FD', 'stock': 5},
                ]
            },
            {
                'name': 'POCKET Urban Flex 6-Pocket Tactical Cargo Pants',
                'category': cat_objs["Bottoms & Denims"],
                'description': 'Engineered for utility and comfort, these 6-pocket cargo trousers feature lightweight stretch twill, reinforced stitching, elasticated waistband with drawstring, and deep utility cargo pockets.',
                'specifications': 'Fabric: 98% Cotton Twill, 2% Elastane | Pockets: 6 Functional Pockets | Fit: Regular Tapered | Waist: Mid-Rise Elasticated',
                'selling_price': Decimal('749.00'),
                'original_price': Decimal('1399.00'),
                'source_cost': Decimal('360.00'),
                'stock_quantity': 28,
                'supplier': s2,
                'is_bestseller': True,
                'is_trending': False,
                'is_featured': True,
                'variants': [
                    {'size': '30', 'color': 'Olive Green', 'color_code': '#365314', 'stock': 6},
                    {'size': '32', 'color': 'Olive Green', 'color_code': '#365314', 'stock': 10},
                    {'size': '34', 'color': 'Olive Green', 'color_code': '#365314', 'stock': 8},
                    {'size': '36', 'color': 'Olive Green', 'color_code': '#365314', 'stock': 4},
                ]
            },
            {
                'name': 'POCKET AirStride Ultralight Breathable Running Sneakers',
                'category': cat_objs["Footwear & Sneakers"],
                'description': 'Walk on clouds with AirStride. Built with high-elasticity EVA cushioned soles and breathable flyknit upper that adapts to your foot stride, providing all-day shock absorption and ventilation.',
                'specifications': 'Upper Material: Breathable Flyknit Mesh | Sole: Shock-absorbing EVA Foam | Closure: Lace-Up | Insole: Cushioned Memory Foam',
                'selling_price': Decimal('899.00'),
                'original_price': Decimal('1699.00'),
                'source_cost': Decimal('420.00'),
                'stock_quantity': 24,
                'supplier': s3,
                'is_bestseller': True,
                'is_trending': True,
                'is_featured': True,
                'variants': [
                    {'size': 'UK 7', 'color': 'Midnight Black', 'color_code': '#0F172A', 'stock': 6},
                    {'size': 'UK 8', 'color': 'Midnight Black', 'color_code': '#0F172A', 'stock': 8},
                    {'size': 'UK 9', 'color': 'Midnight Black', 'color_code': '#0F172A', 'stock': 6},
                    {'size': 'UK 10', 'color': 'Midnight Black', 'color_code': '#0F172A', 'stock': 4},
                ]
            },
            {
                'name': 'POCKET Commuter Water-Resistant Everyday City Backpack',
                'category': cat_objs["Accessories & Bags"],
                'description': 'A streamlined 24-litre commuter backpack with padded 15.6" laptop compartment, anti-theft hidden pocket, durable water-resistant polyester outer shell, and breathable air-mesh shoulder straps.',
                'specifications': 'Capacity: 24 Litres | Laptop Fit: Up to 15.6 inch | Material: 600D Water-Resistant Polyester | Weight: 480 grams',
                'selling_price': Decimal('599.00'),
                'original_price': Decimal('1099.00'),
                'source_cost': Decimal('260.00'),
                'stock_quantity': 40,
                'supplier': s2,
                'is_bestseller': False,
                'is_trending': True,
                'is_featured': True,
                'variants': [
                    {'size': 'Free Size', 'color': 'Charcoal Navy', 'color_code': '#1E293B', 'stock': 40},
                ]
            }
        ]

        # Use the official logo as fallback product photo if no media uploaded
        logo_path = 'static/images/pocket_logo.jpg'

        for p_data in products_data:
            variants = p_data.pop('variants')
            prod, created = Product.objects.get_or_create(
                name=p_data['name'],
                defaults=p_data
            )
            if created:
                # Link primary front photo if available
                front_rel = f"products/{prod.slug}_front.jpg"
                front_full = os.path.join('media', front_rel)
                if os.path.exists(front_full):
                    ProductImage.objects.create(product=prod, image=front_rel, is_primary=True, alt_text=prod.name, display_order=1)
                elif os.path.exists(logo_path):
                    with open(logo_path, 'rb') as f:
                        from django.core.files import File
                        p_img = ProductImage(product=prod, is_primary=True, alt_text=prod.name, display_order=1)
                        p_img.image.save(f"pocket_{prod.id}.jpg", File(f), save=True)

                for v in variants:
                    ProductVariant.objects.create(
                        product=prod,
                        size=v.get('size', ''),
                        color=v.get('color', ''),
                        color_code=v.get('color_code', ''),
                        stock_quantity=v.get('stock', 10)
                    )
            self.stdout.write(f"Product ready: {prod.name}")

        self.stdout.write(self.style.SUCCESS("All seed data created successfully!"))

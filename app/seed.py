"""
Seeds the database with demo categories, products, and an admin user.
Run automatically on startup if SEED_DEMO_DATA=true and the products table is empty.
Can also be run manually: python -m app.seed
"""

from app.database import SessionLocal, engine, Base
from app import models, auth


CATEGORIES = [
    {"name": "Men", "slug": "men", "icon": "ti-shirt"},
    {"name": "Women", "slug": "women", "icon": "ti-dress"},
    {"name": "Electronics", "slug": "electronics", "icon": "ti-device-laptop"},
    {"name": "Footwear", "slug": "footwear", "icon": "ti-shoe"},
    {"name": "Home", "slug": "home", "icon": "ti-sofa"},
    {"name": "Beauty", "slug": "beauty", "icon": "ti-spray"},
]

# Real, freely-licensed product photos (Unsplash) per category.
PRODUCTS = [
    # Men
    {
        "title": "Men slim fit cotton casual shirt",
        "brand": "Roadster",
        "description": "Breathable 100% cotton casual shirt with a slim tailored fit. Machine washable.",
        "price": 899, "mrp": 1499, "stock": 140,
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&q=80",
        "category_slug": "men", "rating": 4.3, "rating_count": 2104,
    },
    {
        "title": "Men relaxed fit denim jacket",
        "brand": "Levi's",
        "description": "Classic trucker-style denim jacket with button front and chest pockets.",
        "price": 2499, "mrp": 3999, "stock": 80,
        "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&q=80",
        "category_slug": "men", "rating": 4.6, "rating_count": 980,
    },
    {
        "title": "Men formal slim trousers",
        "brand": "Van Heusen",
        "description": "Wrinkle-resistant formal trousers, perfect for office wear.",
        "price": 1299, "mrp": 1999, "stock": 110,
        "image_url": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&q=80",
        "category_slug": "men", "rating": 4.1, "rating_count": 540,
    },
    # Women
    {
        "title": "Women floral printed maxi dress",
        "brand": "Zara",
        "description": "Flowy maxi dress with floral print, perfect for summer outings.",
        "price": 1799, "mrp": 2999, "stock": 95,
        "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=600&q=80",
        "category_slug": "women", "rating": 4.5, "rating_count": 1820,
    },
    {
        "title": "Women high-waist denim jeans",
        "brand": "Only",
        "description": "Stretchable high-waist skinny jeans with a flattering fit.",
        "price": 1399, "mrp": 2299, "stock": 130,
        "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&q=80",
        "category_slug": "women", "rating": 4.2, "rating_count": 760,
    },
    {
        "title": "Women quilted handbag",
        "brand": "Caprese",
        "description": "Elegant quilted sling handbag with gold-tone hardware.",
        "price": 1999, "mrp": 3499, "stock": 60,
        "image_url": "https://images.unsplash.com/photo-1591561954557-26941169b49e?w=600&q=80",
        "category_slug": "women", "rating": 4.4, "rating_count": 410,
    },
    # Electronics
    {
        "title": "Wireless over-ear headphones",
        "brand": "SoundWave",
        "description": "Active noise cancelling wireless headphones with 30-hour battery life.",
        "price": 2249, "mrp": 2999, "stock": 200,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
        "category_slug": "electronics", "rating": 4.5, "rating_count": 8732,
    },
    {
        "title": "Smart fitness watch",
        "brand": "Chronotech",
        "description": "AMOLED display smartwatch with heart-rate, SpO2, and 7-day battery.",
        "price": 3499, "mrp": 4999, "stock": 150,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
        "category_slug": "electronics", "rating": 4.4, "rating_count": 5201,
    },
    {
        "title": "27-inch 4K UHD monitor",
        "brand": "ViewPro",
        "description": "Ultra HD IPS monitor with HDR support, ideal for work and gaming.",
        "price": 18999, "mrp": 24999, "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&q=80",
        "category_slug": "electronics", "rating": 4.6, "rating_count": 312,
    },
    {
        "title": "Mechanical gaming keyboard",
        "brand": "KeyForge",
        "description": "RGB backlit mechanical keyboard with hot-swappable switches.",
        "price": 3299, "mrp": 4499, "stock": 90,
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&q=80",
        "category_slug": "electronics", "rating": 4.3, "rating_count": 1190,
    },
    # Footwear
    {
        "title": "Men running shoes",
        "brand": "Stridex",
        "description": "Lightweight breathable mesh running shoes with cushioned sole.",
        "price": 2549, "mrp": 2999, "stock": 170,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80",
        "category_slug": "footwear", "rating": 4.1, "rating_count": 956,
    },
    {
        "title": "Women casual white sneakers",
        "brand": "Bata",
        "description": "Classic white sneakers that pair well with any outfit.",
        "price": 1599, "mrp": 2199, "stock": 140,
        "image_url": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=600&q=80",
        "category_slug": "footwear", "rating": 4.3, "rating_count": 690,
    },
    {
        "title": "Men leather formal shoes",
        "brand": "Clarks",
        "description": "Genuine leather oxford shoes for formal and office wear.",
        "price": 3299, "mrp": 4999, "stock": 75,
        "image_url": "https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=600&q=80",
        "category_slug": "footwear", "rating": 4.5, "rating_count": 420,
    },
    # Home
    {
        "title": "Ceramic coffee mug set of 4",
        "brand": "HomeCraft",
        "description": "Microwave-safe ceramic mugs in assorted pastel colors.",
        "price": 699, "mrp": 999, "stock": 220,
        "image_url": "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=600&q=80",
        "category_slug": "home", "rating": 4.4, "rating_count": 1340,
    },
    {
        "title": "Cotton bedsheet with 2 pillow covers",
        "brand": "Spaces",
        "description": "King-size 300 thread-count cotton bedsheet set with geometric print.",
        "price": 1199, "mrp": 1999, "stock": 100,
        "image_url": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=600&q=80",
        "category_slug": "home", "rating": 4.2, "rating_count": 870,
    },
    {
        "title": "Table lamp with fabric shade",
        "brand": "Lumino",
        "description": "Warm-light bedside table lamp with a wooden base and linen shade.",
        "price": 1499, "mrp": 2299, "stock": 65,
        "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&q=80",
        "category_slug": "home", "rating": 4.3, "rating_count": 305,
    },
    # Beauty
    {
        "title": "Vitamin C brightening serum",
        "brand": "GlowLab",
        "description": "20% Vitamin C serum for brighter, even-toned skin. 30ml.",
        "price": 799, "mrp": 1199, "stock": 250,
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&q=80",
        "category_slug": "beauty", "rating": 4.5, "rating_count": 2980,
    },
    {
        "title": "Matte finish lipstick set",
        "brand": "ColorPop",
        "description": "Long-lasting matte lipstick set, pack of 3 trending shades.",
        "price": 649, "mrp": 999, "stock": 300,
        "image_url": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=600&q=80",
        "category_slug": "beauty", "rating": 4.2, "rating_count": 1540,
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Product).count() > 0:
            print("Database already seeded, skipping.")
            return

        slug_to_category = {}
        for c in CATEGORIES:
            existing = db.query(models.Category).filter(models.Category.slug == c["slug"]).first()
            if not existing:
                existing = models.Category(**c)
                db.add(existing)
                db.flush()
            slug_to_category[c["slug"]] = existing

        for p in PRODUCTS:
            category = slug_to_category[p["category_slug"]]
            product = models.Product(
                title=p["title"],
                brand=p["brand"],
                description=p["description"],
                price=p["price"],
                mrp=p["mrp"],
                stock=p["stock"],
                image_url=p["image_url"],
                category_id=category.id,
                rating=p["rating"],
                rating_count=p["rating_count"],
            )
            db.add(product)

        admin_email = "admin@shopkart.com"
        if not db.query(models.User).filter(models.User.email == admin_email).first():
            admin = models.User(
                name="Admin",
                email=admin_email,
                hashed_password=auth.hash_password("admin123"),
                is_admin=True,
            )
            db.add(admin)

        db.commit()
        print(f"Seeded {len(PRODUCTS)} products across {len(CATEGORIES)} categories.")
        print(f"Admin login -> email: {admin_email}  password: admin123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

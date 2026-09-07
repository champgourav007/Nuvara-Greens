from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Product

PRODUCTS = [
    ("Broccoli Microgreens", "broccoli-microgreens", "Mild, fresh and easy to add to salads, sandwiches and bowls.", "MILD • WELLNESS", "🥦", "broccoli", 50, 80),
    ("Radish Microgreens", "radish-microgreens", "A bright peppery bite for salads, garnishes and everyday meals.", "PEPPERY", "🌱", "radish", 50, 80),
    ("Sunflower Microgreens", "sunflower-microgreens", "Crunchy and satisfying for salads, wraps and nourishing bowls.", "CRUNCHY", "🌻", "sunflower", 100, 150),
    ("Pea Shoots", "pea-shoots", "Sweet, crisp shoots loved by home cooks and chefs alike.", "SWEET • CRUNCHY", "🫛", "pea", 100, 150),
    ("Mustard Microgreens", "mustard-microgreens", "Distinctive flavour for salads, sandwiches and restaurant plating.", "BOLD FLAVOUR", "🌿", "mustard", 50, 80),
    ("NUVARA Mixed Greens", "nuvara-mixed-greens", "A convenient mix for customers who want variety in every pack.", "PREMIUM ASSORTMENT", "🥗", "mix", 50, 90),
]


def seed_products(db: Session):
    if db.scalar(select(Product.id).limit(1)):
        return
    db.add_all([Product(name=n, slug=s, description=d, tag=t, artwork=a, colour=c, unit_weight_g=w, price_inr=p, sort_order=i) for i, (n,s,d,t,a,c,w,p) in enumerate(PRODUCTS)])
    db.commit()

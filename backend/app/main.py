from contextlib import asynccontextmanager
from urllib.parse import quote

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import Enquiry, Order, OrderItem, Product
from .schemas import CheckoutOut, EnquiryCreate, OrderCreate, ProductOut
from .seed import seed_products


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as db:
        seed_products(db)
    yield


app = FastAPI(title="NUVARA GREENS API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health(): return {"status": "ok"}


@app.get("/api/products", response_model=list[ProductOut])
def products(db: Session = Depends(get_db)):
    return db.scalars(select(Product).where(Product.is_active.is_(True)).order_by(Product.sort_order)).all()


@app.post("/api/enquiries", status_code=201)
def create_enquiry(payload: EnquiryCreate, db: Session = Depends(get_db)):
    record = Enquiry(**payload.model_dump())
    db.add(record); db.commit()
    return {"id": str(record.id), "message": "Enquiry received"}


@app.post("/api/orders", response_model=CheckoutOut, status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    ids = [line.product_id for line in payload.items]
    products_by_id = {item.id: item for item in db.scalars(select(Product).where(Product.id.in_(ids), Product.is_active.is_(True))).all()}
    if len(products_by_id) != len(set(ids)):
        raise HTTPException(400, "One or more products are unavailable")
    order = Order(customer_name=payload.customer_name, phone=payload.phone, email=payload.email, subtotal_inr=0)
    for line in payload.items:
        product = products_by_id[line.product_id]
        total = product.price_inr * line.quantity
        order.subtotal_inr += total
        order.items.append(OrderItem(product_id=product.id, product_name_snapshot=product.name, unit_price_inr=product.price_inr, quantity=line.quantity, line_total_inr=total))
    db.add(order); db.commit(); db.refresh(order)
    text = "Hello NUVARA GREENS! I would like to place an order:\n\n" + "\n".join(f"• {i.product_name_snapshot} × {i.quantity} — ₹{i.line_total_inr}" for i in order.items) + f"\n\nTotal: ₹{order.subtotal_inr}\n\nPlease confirm availability and delivery."
    url = None if "X" in settings.whatsapp_number else f"https://wa.me/{settings.whatsapp_number}?text={quote(text)}"
    return CheckoutOut(order_id=order.id, total_inr=order.subtotal_inr, whatsapp_url=url)

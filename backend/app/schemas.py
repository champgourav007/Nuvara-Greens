import uuid
from pydantic import BaseModel, EmailStr, Field


class ProductOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    tag: str
    artwork: str
    colour: str
    unit_weight_g: int
    price_inr: int
    model_config = {"from_attributes": True}


class EnquiryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=6, max_length=40)
    email: EmailStr | None = None
    enquiry_type: str = Field(max_length=50)
    message: str | None = Field(default=None, max_length=2000)


class OrderLineCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=1, le=50)


class OrderCreate(BaseModel):
    items: list[OrderLineCreate] = Field(min_length=1, max_length=30)
    customer_name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None


class CheckoutOut(BaseModel):
    order_id: uuid.UUID
    total_inr: int
    whatsapp_url: str | None

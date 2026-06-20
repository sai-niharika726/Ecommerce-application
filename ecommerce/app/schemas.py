from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Auth / User ----------

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Category ----------

class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    icon: str


# ---------- Product ----------

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    brand: str
    description: str
    price: Decimal
    mrp: Decimal
    stock: int
    image_url: str
    category_id: Optional[int] = None
    rating: Decimal
    rating_count: int
    discount_percent: int = 0


class ProductCreate(BaseModel):
    title: str
    brand: str = ""
    description: str = ""
    price: Decimal
    mrp: Decimal
    stock: int = 100
    image_url: str
    category_id: Optional[int] = None


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    mrp: Optional[Decimal] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


# ---------- Cart ----------

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=20)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=20)


class CartItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product: ProductOut
    quantity: int


# ---------- Address ----------

class AddressCreate(BaseModel):
    full_name: str
    phone: str
    line1: str
    line2: str = ""
    city: str
    state: str
    pincode: str
    is_default: bool = False


class AddressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    phone: str
    line1: str
    line2: str
    city: str
    state: str
    pincode: str
    is_default: bool


# ---------- Orders ----------

class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title_snapshot: str
    image_snapshot: str
    price_snapshot: Decimal
    quantity: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    items: list[OrderItemOut]


class CheckoutRequest(BaseModel):
    address_id: int


# ---------- Reviews ----------

class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = ""


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rating: int
    comment: str
    user_name: str
    created_at: datetime

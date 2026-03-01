import enum 

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy import ( String, Integer, ForeignKey, DateTime, Boolean, Numeric, Enum as SAEnum, Text )
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from ..db.database import Base 

class RoleEnum(str, enum.Enum): 
    user = "user"
    admin = "admin"

class User(Base): 
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[RoleEnum] = mapped_column(SAEnum(RoleEnum), default=RoleEnum.user)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    referrals: Mapped[List["Referral"]] = relationship(back_populates="user")

class Category(Base): 
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(150), index=True)
    slug: Mapped[Optional[str]] = mapped_column(String(150), unique=True)

    products: Mapped[List["Product"]] = relationship(back_populates="category")

class Merchant(Base): 
    __tablename__ = "merchant"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(150))
    website_url: Mapped[int] = mapped_column(String(255))
    logo_url: Mapped[Optional[str]] = mapped_column(String(255))

    offers: Mapped[List["Offer"]] = relationship(back_populates="merchant")

class Product(Base): 
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    brand_name: Mapped[Optional[str]] = mapped_column(String(150))
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(String(255))

    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("category.id"))

    category: Mapped[Optional["Category"]] = relationship(back_populates="products")
    offers: Mapped[List["Offer"]] = relationship(back_populates="product")

class Offer(Base):
    __tablename__ = "offer"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchant.id"))

    affiliate_url: Mapped[str] = mapped_column(String(500))

    original_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    current_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    discount_percent: Mapped[float] = mapped_column(default=0)

    is_in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    last_scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="offers")
    merchant: Mapped["Merchant"] = relationship(back_populates="offers")

    price_history: Mapped[List["PriceHistory"]] = relationship(back_populates="offer")
    referrals: Mapped[List["Referral"]] = relationship(back_populates="offer")

class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[int] = mapped_column(ForeignKey("offer.id"))

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    offer: Mapped["Offer"] = relationship(back_populates="price_history")

class Referral(Base):
    __tablename__ = "referral"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"))
    offer_id: Mapped[int] = mapped_column(ForeignKey("offer.id"))

    clicked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))

    user: Mapped[Optional["User"]] = relationship(back_populates="referrals")
    offer: Mapped["Offer"] = relationship(back_populates="referrals")

class RedirectResponse(Base):
    __tablename__ = "redirect_response"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(500))
    status_code: Mapped[int] = mapped_column(Integer)
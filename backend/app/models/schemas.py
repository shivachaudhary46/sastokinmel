from pydantic import BaseModel, field_validator, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum 
from decimal import Decimal

class Role(str, Enum): 
    user = "user"
    admin = "admin"

class UserCreate(BaseModel):
    username: str 
    full_name: str 
    email: EmailStr
    password: str 

class UserResponse(BaseModel): 
    id: int 
    username: str
    full_name: str
    email: EmailStr
    role: Role
    created_at: datetime

    class Config: 
        from_attributes = True 

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None   

class CategoryCreate(BaseModel):
    name: str
    slug: str 

class CategoryResponse(BaseModel):
    id: int
    name: str 
    slug: str 

    class Config: 
        from_attributes = True 
    
class MerchantCreate(BaseModel):
    name: str
    website_url: str
    logo_url: Optional[str] = None
    
class MerchantResponse(BaseModel):
    id: int 
    name: str 
    website_url: str 
    logo_url: Optional[str]

    model_config = {
        "from_attributes": True 
    }

class OfferResponse(BaseModel): 
    id: int 
    affiliate_url: str
    original_price: Decimal
    current_price: Decimal 
    discount_percent: float
    is_in_stock: bool
    last_scraped_at: datetime

    Merchant: Optional[MerchantResponse] = None 

    model_config = {
        "from_attributes": True
    }


class ProductCreate(BaseModel):
    name: str 
    brand_name: Optional[str] = None 
    description: Optional[str] = None 
    image_url: str 
    category_id: int

class ProductResponse(BaseModel):
    id: int 
    name: str 
    brand_name: Optional[str]
    description: Optional[str]
    image_url: str 
    category: Optional[CategoryResponse]
    offer: Optional[OfferResponse] = None 

class OfferCreate(BaseModel): 
    product_id: int 
    merchant_id: int 
    affiliate_url: str
    original_price: Decimal 
    current_price: Decimal
    discount_percent: float
    is_in_stock: bool = True

class PriceHistoryResponse(BaseModel): 
    price: Decimal 
    recorded_at: datetime

    model_config = {
        "from_attributes": True 
    }

class ReferralCreate(BaseModel): 
    user_id: int 
    offer_id: int
    ip_address: Optional[str] = None 
    user_agent: Optional[str] = None

class ReferralResponse(BaseModel): 
    id: int
    user_id: int 
    offer_id: int
    clicked_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]

    model_config = {
        "from_attributes": True 
    }
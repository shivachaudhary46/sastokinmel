# ===== Import necessary libraries =====
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from typing import Optional, List
from fastapi import HTTPException 

from backend.app.models.schemas import UserResponse, MerchantCreate, MerchantResponse
from backend.app.models.models import User, Referral, Category, Product, Merchant, Offer

# ====== User Operations =======
def get_user_by_username(session: Session, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    return session.scalars(statement).first()

def get_user_by_user_id(session: Session, id: str) -> Optional[UserResponse]: 
    statement = session.get(User, id)
    return statement

def create_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_all_users(session: Session, role: str, skip: int = 0, limit: int = 100) -> List[User]:
    """Fetch all users"""
        
    statement = select(User).offset(skip).limit(limit)
    if role:
        statement = statement.where(User.role == role)
    users = session.scalars(statement).all()
    return users

def delete_user_by_id(session: Session, user_id: int):

    links = session.scalars(
        select(Referral).where(Referral.user_id == user_id)
    ).all()

    for link in links:
        session.delete(link)

    user = session.get(User, user_id)
    if not user:
        return False

    session.delete(user)
    session.commit()
    return True

# ====================== Categories Operations 
def get_category_by_name(session: Session, category_name: str) -> Optional[Category]:
    statement = select(Category).where(Category.name == category_name)
    return session.scalars(statement).first() 

def create_category(session: Session, category: Category) -> Category: 
    session.add(category)
    session.commit() 
    session.refresh(category)
    return category

def get_all_category(session: Session) -> List[Category]:
    result = session.scalars(select(Category)).all()
    return result

def get_all_products_by_category(
    session: Session,
    slug: str,
    skip: int = 0,
    limit: int = 10
) -> List[Product]:
    """
    Fetch all products belonging to a category identified by slug
    """

    statement = (
        select(Product)
        .join(Category)
        .where(Category.slug == slug)
        .offset(skip)
        .limit(limit)
    )

    products = session.scalars(statement).all()
    return products

# ============== Product ===========
def get_existing_product(session: Session, product_name: str) -> Product: 
    statement = select(Product).where(Product.name == product_name)
    return session.scalars(statement).first()

def create_product(session: Session, product: Product) -> Product: 
    session.add(product)
    session.commit() 
    session.refresh(product)
    return product

# ======== offer =========
def create_offer(session: Session, offer: Offer) -> Offer: 
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer 

def get_exisiting_offer(session: Session, product_id: int) -> Offer: 
    statement = select(Offer).where(Offer.product_id == product_id)
    return session.scalars(statement).first()

def get_existing_referral(session: Session, offer_id: int) -> Referral:
    statement = select(Referral).where(Referral.offer_id == offer_id)
    return session.scalars(statement).first()

def create_referral(session: Session, referral: Referral) -> Referral: 
    session.add(referral)
    session.commit()
    session.refresh(referral)
    return referral

# ========== create all merchant helper functions ==============
def get_merchant_by_merchantname(session: Session, merchant_name: str) -> Merchant:
    statement = select(Merchant).where(Merchant.name == merchant_name)
    return session.scalars(statement).first()

def create_merchant(session: Session, merchant: Merchant) -> Merchant: 
    session.add(merchant)
    session.commit()
    session.refresh(merchant)
    return merchant

def get_all_merchant(session: Session) -> Merchant: 
    statement = select(Merchant)
    return session.scalars(statement).all()

def get_merchant_by_id(session: Session, merchant_id: str) -> Merchant: 
    statement = select(Merchant).where(Merchant.merchant_id == merchant_id)
    return session.scalars(statement).first()

def update_merchant(session: Session, merchant_id: str, merchant_data: MerchantCreate) -> MerchantResponse: 
    merchant = session.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(404, "Merchant not found")

    merchant.name = merchant_data.name
    merchant.logo_url = merchant_data.logo_url
    merchant.website_url = merchant_data.website_url

    session.add(merchant)
    session.commit()
    session.refresh(merchant)
    return merchant

def delete_merchant_by_id(session: Session, merchant_id: int) : 
    """Delete Merchant by ID"""

    merchant = session.get(Merchant, merchant_id)
    if not merchant: 
        raise HTTPException(404, "Merchant not found")
    
    session.delete(merchant)
    session.commit()
    return {"Message": "Merchant deleted successfully"}

def get_existing_all_product(session: Session) -> Product: 
    statement = select(Product)
    return session.scalars(statement).all()

def get_all_offer_on_product(session: Session, product_id: int) -> Product: 
    statement = select(Offer).where(Offer.product_id == product_id)
    return session.scalars(statement).all()
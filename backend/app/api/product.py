from fastapi import APIRouter, HTTPException, Depends
from app.db.database import SessionDep
from app.models.models import User, Product, Offer, Referral
from app.models.schemas import ProductCreate, ProductResponse, OfferCreate, OfferResponse, ReferralResponse, ReferralCreate
from app.auth.oauth import role_required
from app.loggers.logger import logger
from app.utilities.crud import get_existing_product, create_product, create_offer, get_exisiting_offer, get_existing_referral, create_referral 

router = APIRouter(
    prefix="/product",
    tags=["product"]
)

@router.post("/", response_model=ProductResponse)
def create_new_product(product_data: ProductCreate, session: SessionDep, user: User = Depends(role_required(["admin"]))):
    """Create a new category for admin only access"""
    try:
        existing = get_existing_product(session, product_data.name)
        if existing:
            logger.debug(f"name {product_data.name} already exists")
            raise HTTPException(status_code=400, detail="Product already exists")

        instance = Product(
            name = product_data.name,
            brand_name = product_data.brand_name, 
            description = product_data.description, 
            image_url = product_data.image_url,
            category_id= product_data.category_id,
        )

        logger.debug(f"Product instance created {instance}")
        new_product = create_product(session, instance)

        logger.debug(f"Product created successfully: {Product.name}")
        return new_product

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error creating categories: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/offer", response_model=OfferResponse)
def create_offer_with_product(offer_data: OfferCreate, session: SessionDep, user: User = Depends(role_required(["admin"]))):
    """Create a new offer with the different merchant"""

    try: 
        existing_offer = get_exisiting_offer(session, offer_data.product_id)
        if existing_offer: 
            logger.debug(f"offer {offer_data.product_id} already existed")
            raise HTTPException(status_code=400, detail="Offer Already Exists")

        instance = Offer(
            product_id = offer_data.product_id,
            merchant_id = offer_data.merchant_id, 
            affiliate_url = offer_data.affiliate_url, 
            original_price = offer_data.original_price,
            current_price = offer_data.current_price, 
            discount_percent = offer_data.discount_percent, 
            is_in_stock = offer_data.is_in_stock 
        )

        logger.debug(f"Offer instance created {instance}")
        new_offer = create_offer(session, instance)

        logger.debug(f"offer created successfully: {new_offer}")
        return new_offer

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error creating offer: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
 
@router.post("/referral", response_model=ReferralResponse)
def create_referral_with_product(referral_data: ReferralCreate, session: SessionDep, user: User = Depends(role_required(["admin"]))):
    """when a user buys product it will get referral"""

    try: 
        existing_offer = get_existing_referral(session, referral_data.offer_id)
        if existing_offer: 
            logger.debug(f"offer {referral_data.offer_id} already existed")
            raise HTTPException(status_code=400, detail="referral Already Exists")

        instance = Referral(
            user_id = referral_data.user_id,
            offer_id = referral_data.offer_id, 
            ip_address = referral_data.ip_address,
            user_agent = referral_data.user_agent, 
        )

        logger.debug(f"Referral instance created {instance}")
        new_referral = create_referral(session, instance)

        logger.debug(f"referral created successfully: {new_referral}")
        return new_referral

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error creating offer: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


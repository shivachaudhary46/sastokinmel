from fastapi import APIRouter, HTTPException, Depends
from app.db.database import SessionDep
from typing import List
from app.models.schemas import MerchantCreate, MerchantResponse
from app.models.models import User, Merchant
from app.auth.oauth import role_required
from app.utilities.crud import get_merchant_by_merchantname, create_merchant, get_all_merchant, get_merchant_by_id, update_merchant, delete_merchant_by_id
from app.loggers.logger import logger

router = APIRouter(
    prefix="/merchant",
    tags=["merchant"]
)

@router.post("/", response_model=MerchantResponse)
def create_new_merchant(merchant_data: MerchantCreate, session: SessionDep, user: User = Depends(role_required(["admin"]))):
    """Create a new merchant for admin only access"""
    try:
        existing = get_merchant_by_merchantname(session, merchant_data.name)
        if existing:
            logger.debug(f"merchant name {merchant_data.name} already exists")
            raise HTTPException(status_code=400, detail="Merchant already exists")

        instance = Merchant(
            name = merchant_data.name, 
            website_url = merchant_data.website_url,
            logo_url = merchant_data.logo_url,
        )

        logger.debug(f"Merchant instance created {instance}")
        new_merchant = create_merchant(session, instance)

        logger.debug(f"Merchant created successfully: {Merchant.name}")
        return new_merchant

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# GET ALL MERCHANT
@router.get("/", response_model=List[MerchantResponse])
def get_merchant(session: SessionDep):
    try:
        all_merchant = get_all_merchant(session)
        logger.info(f"Successfully fetched all merchant")
        return all_merchant    
    except Exception as e:
        logger.error(f"Unexpected error while fetching merchant: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# GET merchant BY merchant Id
@router.get("/{merchant_id}", response_model=MerchantResponse)
def get_merchant_by_id_endpoints(session: SessionDep, merchant_id: int):
    try:
        merchant = get_merchant_by_id(session, merchant_id)
        if not merchant:
            logger.warning(f"merchant not found for {merchant_id}")
            raise HTTPException(status_code=404, detail="merchant not found")
        return merchant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching fees: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Update Merchant
@router.put("/{merchant_id}", response_model=MerchantResponse)
def update_merchant_endpoints(
    merchant_id: int,
    merchant_data: MerchantCreate,
    session: SessionDep,
    user: User = Depends(role_required(["admin"]))
):
    try:
        merchant = update_merchant(session, merchant_id, merchant_data)
        if not merchant:
            logger.warning(f"Successfully updated merchant for {merchant_id}")
            raise HTTPException(status_code=404, detail="merchant not found")
        return merchant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while updating merchant: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# DELETE merchant
@router.delete("/{merchant_id}")
def delete_merchant_by_merchant_id_endpoints(
    merchant_id: int,
    session: SessionDep,
    user: User = Depends(role_required(["admin"]))
):
    try:
        if not delete_merchant_by_id(session, merchant_id):
            logger.warning(f"Merchant could not found for {merchant_id}")
            raise HTTPException(status_code=404, detail="merchant not found")
        return {"message": "merchant deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while deleting merchant: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
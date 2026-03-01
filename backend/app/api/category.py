from fastapi import APIRouter, HTTPException, Depends, Query
from backend.app.db.database import SessionDep
from backend.app.models.schemas import CategoryCreate, CategoryResponse
from backend.app.models.models import User, Category
from backend.app.auth.oauth import role_required
from backend.app.utilities.crud import get_category_by_name, create_category, get_all_category
from backend.app.loggers.logger import logger
from typing import List

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.post("/", response_model=CategoryResponse)
def create_new_category(category_data: CategoryCreate, session: SessionDep, user: User = Depends(role_required(["admin"]))):
    """Create a new category for admin only access"""
    try:
        existing = get_category_by_name(session, category_data.name)
        if existing:
            logger.debug(f"name {category_data.name} already exists")
            raise HTTPException(status_code=400, detail="Category already exists")

        instance = Category(
            name = category_data.name,
            slug = category_data.slug,
        )

        logger.debug(f"Category instance created {instance}")
        new_category = create_category(session, instance)

        logger.debug(f"Category created successfully: {Category.name}")
        return new_category

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error creating categories: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get all category listed on this 
@router.get("/", response_model=List[CategoryResponse])
def read_all_category(session: SessionDep):
    """Get all Category"""
    try: 
        all_category = get_all_category(session)
        logger.info("All category fetched successfully.")
        return all_category
    except Exception as e: 
        logger.error(f"Error while fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get category page by slug (testing phase)
# Need to add Pagination (page & limit) controls how many products are returned
@router.get("/{slug}", response_class=List[CategoryResponse])
def get_category_by_slug(slug: str, session: SessionDep): 
    pass 

# Slug uses is base_url/categories/{slug} here, slug = skin-care, lip-balm, slug should be meaningful in realworld, and permanent 
# we will assume slug as categories, so we will try to fetch every product in that slug (category), 
# Pagination, limitation 
# @router.get("/{slug}/product")
# def get_all_product_from_slug(
#     session: SessionDep,
#     page: int = 1,
#     skip: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
#     ):
#     """Get all users"""
#     try:
#         all_products = get_all_products_by_category(session, page, skip, limit)
#         logger.info("All users fetched successfully.")
#         return all_products

#     except Exception as e:
#         logger.error(f"Error while fetching users: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# Total count of product listed on that slug / categories 
# @router.get("/{slug}/product/total")
# def get_total_product_under_categories(session: SessionDep, page: int = 1, skip: int = 0, limit: Annotated[int, Query(le=100)] = 100):
#     try: 
#         total_product = get_total_count_product(session, skip, limit)
#         return total_product
    
#     except Exception as e: 
#         raise HTTPException (status_code=500, detail="Internal Server Error")

# Update categories (name only, slug will be never updated, admin only)

'''
API Endpoints for categories

POST - / (create new category)
GET - /  (return all categories)
GET - /{slug}/ (get category page by slug)
GET - /{slug}/product (get all product from slug / categories)
GET - /{slug}/product/total (total count of product from that slug)

GET - /{slug}/product/offers (return all products offers with categories)
'''


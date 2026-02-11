from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
from app.db.database import SessionDep
from app.models.schemas import CategoryCreate, CategoryResponse
from app.models.models import User, Category
from app.auth.oauth import role_required
from app.utilities.crud import get_category_by_name, create_category, get_all_products_by_category
from app.loggers.logger import logger
from typing import Annotated

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


# # Testing phase 
# @router.get("/", response_model=List[CategoryResponse])
# def read_all_category(session: SessionDep):
#     """Get all Category"""
#     try: 
#         all_category = get_all_category(session)
#         logger.debug("All category fetched successfully.")
#         return all_category
#     except Exception as e: 
#         logger.debug(f"Error while fetching categories: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# # Get category page by slug (testing phase)
# # Slug is used for SEO-friendly URLs
# # Base URL: /categories/{slug}
# # Example: /categories/skin-care
# # Slug identifies the category whose products we want to fetch
# # Pagination (page & limit) controls how many products are returned

# # Slug uses is base_url/categories/{slug} here, slug = skin-care, lip-balm, slug should be meaningful in realworld, and permanent 
# # here, we will assume slug as categories, so we will try to fetch every product in that slug (category), 
# @router.get("/categories/{slug}")
# def get_product_from_slug(
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


# # POST request creating the categories for only admin 
# # READ all categories 
# # Access Category page by slug (SEO handling)
# # READ how many products under a category 
# @router.get("/categories/{slug}/product")
# def get_total_product_under_categories(session: SessionDep, page: int = 1, skip: int = 0, limit: Annotated[int, Query(le=100)] = 100):
#     try: 
#         total_product = get_total_count_product(session, skip, limit)
#         return total_product
    
#     except Exception as e: 
#         raise HTTPException (status_code=500, detail="Internal Server Error")

# # Admin-only update (name only, never slug)
# # Get category page by slug 

# # Get products inside a category (with pagination)
# # Get product page by slug 

# # Homepage -> GET / categories
# # Category page 
# # GET /categories/{slug}
# # GET /categories/{slug}/products
# # product page 
# # Get / products/{slug}
# # Get / products/{slug}/offers
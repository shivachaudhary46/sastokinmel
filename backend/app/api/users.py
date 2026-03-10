from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Annotated, Optional
from backend.app.models.models import User
from backend.app.db.database import SessionDep
from backend.app.models.schemas import UserCreate, UserResponse
from backend.app.utilities.crud import ( get_user_by_username, create_user, get_all_users, delete_user_by_id, )
from backend.app.auth.oauth import get_current_user, authenticate_user
from pwdlib import PasswordHash 
from ..loggers.logger import logger

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

hasher = PasswordHash.recommended()

'''
USERS 
GET    /users/                  - Get all username
GET    /users/{username}        - Get userdetails by username 
POST   /users/                  - Create new users
PUT    /users/                  - Update referral
DELETE /users/{username}        - Delete referral
'''

# Create User
@router.post("/", response_model=UserResponse)
def create_new_user(user_data: UserCreate, session: SessionDep):
    """Create a new user"""
    try:

        existing = get_user_by_username(session, user_data.username)
        if existing:
            logger.warning(f"Username {user_data.username} already exists")
            raise HTTPException(status_code=400, detail="Username already exists")

        user = User(
            username=user_data.username,
            full_name=user_data.full_name,
            email=user_data.email,
            password=hasher.hash(user_data.password)
        )

        new_user = create_user(session, user)

        logger.info(f"User created successfully: {user_data.username}")
        return new_user

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/", response_model=UserResponse)
def update_password(
    old_password: str,
    new_password: str, 
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep
):
    """Update a password"""
    try:
        auth_user = authenticate_user(session, current_user.username, old_password)
        if not auth_user:
            logger.info(f"User {current_user.id} not found for update or password doesn't match")
            raise HTTPException(status_code=404, detail="password does not match")
        
        current_user.password = hasher.hash(new_password)
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        logger.info(f"password of {current_user.id} updated successfully by user {current_user.id}")
        return current_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while updating user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get all users
@router.get("/", response_model=List[UserResponse])
def read_all_users(
    session: SessionDep,
    role: Optional[str] = None,
    skip: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    """Get all users"""
    try:
        all_users = get_all_users(session, role, skip, limit)
        logger.info("All users fetched successfully.")
        return all_users

    except Exception as e:
        logger.error(f"Error while fetching users: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get a user by username
@router.get("/{username}", response_model=UserResponse)
def read_user(username: str, session: SessionDep):
    """Get a specific user by username"""
    try:
        user = get_user_by_username(session, username)

        if not user:
            logger.warning(f"User '{username}' not found")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"User '{username}' fetched successfully")
        return user

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error fetching user '{username}': {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Delete a user by username
@router.delete("/{username}")
def delete_user_by_username(username: str, session: SessionDep):
    """Delete a user"""
    try:
        user = get_user_by_username(session, username)

        if not user:
            logger.warning(f"User '{username}' not found")
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")

        delete_user_by_id(session, user.id)

        logger.info(f"User '{username}' deleted successfully")
        return {"ok": True}

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error while deleting user '{username}': {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

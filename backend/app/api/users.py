from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Annotated, Optional

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

from app.models.models import User
from app.db.database import SessionDep
from app.models.schemas import UserCreate, UserResponse
from app.utilities.crud import (
    get_user_by_username, create_user, get_all_users, delete_user_by_id, 
)
from app.auth.oauth import get_current_user, authenticate_user

from pwdlib import PasswordHash 

hasher = PasswordHash.recommended()

# @router.post("/admin")
# def create_admin(session: SessionDep): 
#     user_data1 = UserCreate(
#         username="shivachaudhary",
#         full_name="shiva chaudhary", 
#         email="shivachaudhary4116@gmail.com",
#         password="$argon2id$v=19$m=65536,t=3,p=4$6K7I9D8USPqkqf9CTcuBlw$fmB+5XjNhuVxonRu8mMmbY7G/1u+uAkbqD7cemil5VYhash", 
#     )
#     user_data2 = UserCreate(
#         username="chandansharma", 
#         email="chandansha198@gmail.com",
#         full_name="Chandan Sharma Thakur", 
#         password="$argon2id$v=19$m=65536,t=3,p=4$76dFUng28Em3Beohh4H1tg$0leC7cuJAaNjugSL3L6sctDWIQWSelZHpJ3TB0lTd0Y"
#     )

#     admin1 = User(
#         role="admin", 
#         username=user_data1.username,
#         email=user_data1.email,
#         full_name=user_data1.full_name,
#         password=user_data1.password,
#     )

#     admin2 = User(
#         role="admin", 
#         username=user_data2.username,
#         email=user_data2.email,
#         full_name=user_data2.full_name,
#         password=user_data2.password,
#     )

#     create1 = create_user(session, admin1)
#     create2 = create_user(session, admin2)

#     return create1, create2

# Create User
@router.post("/", response_model=UserResponse)
def create_new_user(user_data: UserCreate, session: SessionDep):
    """Create a new user"""
    try:

        existing = get_user_by_username(session, user_data.username)
        if existing:
            print(f"Username {user_data.username} already exists")
            raise HTTPException(status_code=400, detail="Username already exists")

        user = User(
            username=user_data.username,
            full_name=user_data.full_name,
            email=user_data.email,
            password=hasher.hash(user_data.password)
        )

        new_user = create_user(session, user)

        print(f"User created successfully: {user_data.username}")
        return new_user

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error creating user: {e}")
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
            print(f"User {current_user.id} not found for update or password doesn't match")
            raise HTTPException(status_code=404, detail="password does not match")
        
        current_user.password = hasher.hash(new_password)
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        print(f"password of {current_user.id} updated successfully by user {current_user.id}")
        return current_user
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error while updating user {current_user.id}: {e}")
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
        print("All users fetched successfully.")
        return all_users

    except Exception as e:
        print(f"Error while fetching users: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Get a user by username
@router.get("/{username}", response_model=UserResponse)
def read_user(username: str, session: SessionDep):
    """Get a specific user by username"""
    try:
        user = get_user_by_username(session, username)

        if not user:
            print(f"User '{username}' not found")
            raise HTTPException(status_code=404, detail="User not found")

        print(f"User '{username}' fetched successfully")
        return user

    except HTTPException:
        raise

    except Exception as e:
        print(f"Unexpected error fetching user '{username}': {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Delete a user by username
@router.delete("/{username}")
def delete_user_by_username(username: str, session: SessionDep):
    """Delete a user"""
    try:
        user = get_user_by_username(session, username)

        if not user:
            print(f"User '{username}' not found")
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")

        delete_user_by_id(session, user.id)

        print(f"User '{username}' deleted successfully")
        return {"ok": True}

    except HTTPException:
        raise

    except Exception as e:
        print(f"Unexpected error while deleting user '{username}': {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

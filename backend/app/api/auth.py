# auth.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
import os
from dotenv import load_dotenv

from app.models.schemas import Token, UserResponse
from app.models.models import User
from app.auth.oauth import authenticate_user, create_access_token, get_current_user
from app.db.database import SessionDep

load_dotenv()
ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE", 60))

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/token", response_model=Token)
async def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
):
    try:
        """
        Authenticate a user and return an access token.
        """
        print(f"Login attempt by username: {credentials.username}")

        user = authenticate_user(session, credentials.username, credentials.password)

        if not user:
            print(f"Failed login attempt invalid credentials for user: {credentials.username}")
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        # logger.info(f"Found user with {user.username}")
        access_time = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
        # logger.info(f"given time = {access_time}")
        token = create_access_token(
            data={"sub": user.username},
            expire_time=access_time
        )

        print(f"Login successful for user: {user.username}")

        return Token(access_token=token, token_type="bearer")
    
    except HTTPException:
        raise

    except Exception as e:
        print(
            f"Unexpected server error during login for user {credentials.username}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    try: 
        """
        Return the currently authenticated user's information.
        """
        print(f"/me accessed by user: {current_user.username}")
        return current_user
    except: 
        print(f"Unexpected error occurred while login.")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

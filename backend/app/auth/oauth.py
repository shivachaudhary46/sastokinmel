import jwt
import os
from sqlalchemy import select
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from typing import Union

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from backend.app.db.database import SessionDep
from backend.app.models.models import User
from backend.app.models.schemas import TokenData
from typing import Annotated
from backend.app.config import settings
load_dotenv()

secret_key = os.getenv("secret_key")
ALGO = os.getenv("ALGO")

oauth_scheme2 = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_user(username: str, session: SessionDep) -> User:
    statement = select(User).where(User.username == username)
    results = session.scalars(statement)
    account = results.first()

    if not account:
        return None

    return account

def authenticate_user(session: SessionDep, username: str, password: str) :
    user = get_user(username, session)

    from pwdlib import PasswordHash
    hasher = PasswordHash.recommended()

    if not user:
        print("Username not found in database")
        return None
    if not isinstance(password, str):
        print(f"Password is not a string for username {username} ")
        return none
    if not hasher.verify(password, user.password):
        print(f"Password not matched of username {username}")
        return None 
    return user

def create_access_token(data: dict, expire_time: Union[timedelta, None] = None):
    to_encode = data.copy()
    
    if expire_time:
        expire = datetime.now(timezone.utc) + expire_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    # Add validation
    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY is not configured")
    
    # logger.error(f"JWT PAYLOAD → sub='{to_encode.get('sub')}' ({type(to_encode.get('sub'))})")
    # logger.error(f"JWT PAYLOAD → exp={to_encode.get('exp')} ({type(to_encode.get('exp'))})")
    # logger.error(f"JWT SECRET → {settings.SECRET_KEY!r} ({type(settings.SECRET_KEY)})")
    # logger.error(f"JWT ALGO → {settings.ALGO!r} ({type(settings.ALGO)})")
    
    encoded_jwt = jwt.encode(
        to_encode, 
        str(settings.SECRET_KEY),  # Ensure it's a string
        algorithm=settings.ALGO
    )
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth_scheme2)], session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Use SECRET_KEY (uppercase) - same as in create_access_token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGO])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return user

def role_required(allowed_roles: list):
    def wrapper(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        return current_user
    return wrapper
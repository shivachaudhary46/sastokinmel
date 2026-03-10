from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from backend.app.config import settings
from typing import Annotated
from fastapi import Depends

URL_DATABASE = settings.DATABASE_URL
engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally: 
        db.close() 

def create_table(): 
    Base.metadata.create_all(bind=engine)

SessionDep = Annotated[Session, Depends(get_db)]
from typing import Annotated
from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session 

sqlite_url = "sqlite:///database.url"

engine = create_engine(sqlite_url)

def create_all_db_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session: 
        yield session

SessionDep = Annotated[Session, Depends(get_session)] 

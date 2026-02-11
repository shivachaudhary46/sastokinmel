from contextlib import asynccontextmanager
from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import create_db_and_tables
from app.api import (
    users, auth, categories, product, merchant
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Sasto Kinmel",
    description="sasto kinmel",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

@app.get("/")
def root(): 
    return {"message": "Sasto Kinmel", "status": "running"}

@app.get("/health")
def health_check(): 
    return {
        "status": "healthy", 
    }

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(product.router)
app.include_router(merchant.router)

if __name__ == "__main__": 
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        reload_excludes=["backend/logs/*"]
    )
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db


# ----------------------------------------
# 1. ROUTER — like a mini FastAPI app
# ----------------------------------------
router = APIRouter(
    prefix="/api/v1",       # all routes start with /api/v1
    tags=["Health"]         # groups in Swagger UI
)


# ----------------------------------------
# 2. HEALTH CHECK endpoint
# ----------------------------------------
@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # tries to run simple query on DB
    await db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "app": "DocSense AI",
        "database": "connected."
    }

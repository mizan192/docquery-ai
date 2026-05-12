from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import health, documents, search          # ← import router
from app.database import init_db        # ← import init_db
from app.models import document       # ← import document model (creates table on startup)
from app.core.logging import logger


# ----------------------------------------
# 1. LIFESPAN — startup & shutdown
# ----------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — runs when server starts
    logger.info("Starting DocSense AI")
    await init_db()
    logger.info("Database connected")
    
    # app runs here
    yield                   

    # SHUTDOWN — runs when server stops
    logger.info("Shutting down DocSense AI")


# ----------------------------------------
# 2. CREATE FastAPI APP
# ----------------------------------------
app = FastAPI(
    title="DocSense AI",
    description="AI Powered Document Search System",
    version="1.0.0",
    lifespan=lifespan
)


# ----------------------------------------
# 3. REGISTER ROUTERS
# ----------------------------------------
app.include_router(health.router)
app.include_router(documents.router)   
app.include_router(search.router)


# ----------------------------------------
# 4. ROOT endpoint
# ----------------------------------------
@app.get("/")
async def root():
    return {
        "app": "DocSense AI",
        "version": "1.0.0",
        "status": "running.",
        "docs": "/docs"
    }

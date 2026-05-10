from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import health, documents, search          # ← import router
from app.database import init_db        # ← import init_db
from app.models import document       # ← import document model (creates table on startup)

# ----------------------------------------
# 1. LIFESPAN — startup & shutdown
# ----------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — runs when server starts
    await init_db()
    print("Database connected")
    print("DocSense AI is ready")

    yield                   # ← app runs here

    # SHUTDOWN — runs when server stops
    print("Shutting down DocSense AI")


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

from fastapi import FastAPI
from app.routers import health
from app.database import engine, Base

app = FastAPI(title="RAG Q&A System", version="1.0.0")

app.include_router(health.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "RAG Backend is running 🚀"}
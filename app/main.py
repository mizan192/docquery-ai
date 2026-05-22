from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import health, documents, search, auth        # ← import router
from app.database import init_db        # ← import init_db
from app.models import document       # ← import document model (creates table on startup)
from app.core.logging import logger
from fastapi.openapi.utils import get_openapi



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
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True}  # keeps token after restart
)


# ----------------------------------------
# 3. REGISTER ROUTERS
# ----------------------------------------
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)   
app.include_router(search.router)


# add bearer token support to swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="DocQuery AI",
        version="1.0.0",
        description="AI Powered Document Search System",
        routes=app.routes,
    )

    # add bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # apply security to all endpoints
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


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

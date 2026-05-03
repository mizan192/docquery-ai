from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import text
from app.config import settings

# ----------------------------------------
# 1. ENGINE — connects to PostgreSQL
# ----------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG        # prints SQL in terminal when DEBUG=True
)

# ----------------------------------------
# 2. SESSION — handles DB conversations
# ----------------------------------------
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ----------------------------------------
# 3. BASE — parent for all DB tables
# ----------------------------------------
Base = declarative_base()

# ----------------------------------------
# 4. Initialize DB — runs on app startup
# ----------------------------------------
async def init_db():
    async with engine.begin() as conn:

        # Enable pgvector extension in PostgreSQL
        # This adds vector data type support
        # IF NOT EXISTS = safe to run multiple times
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # Create all tables defined in models/
        # SQLAlchemy reads your models and creates tables automatically
        await conn.run_sync(Base.metadata.create_all)

# ----------------------------------------
# 5. get_db() — gives DB session to routers
# ----------------------------------------
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

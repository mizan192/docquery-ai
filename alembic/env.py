from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# add app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import base
from app.database import Base

# just import models module
# this triggers __init__.py automatically
import app.models

config = context.config
fileConfig(config.config_file_name)

# this tells alembic about your DB tables
target_metadata = Base.metadata


def get_url():
    """
    reads DATABASE_URL from environment
    works both locally and in Docker automatically
    local  -> uses localhost
    Docker -> uses db container name
    """
    from app.config import settings
    # alembic needs psycopg2 not asyncpg
    return settings.DATABASE_URL.replace(
        "postgresql+asyncpg",
        "postgresql+psycopg2"
    )


# Offline mode: Generates raw SQL scripts without connecting to a live database.
# Best for dry-runs (e.g. alembic upgrade head --sql) or generating SQL for DBAs.
def run_migrations_offline() -> None:
    # use get_url() instead of config url
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# Online mode: Connects directly to the database and applies migrations.
# Runs changes inside a safe transaction that rolls back if an error occurs.
def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})

    # override sqlalchemy.url with environment variable
    # this makes it work both locally and in Docker
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool
    )
    with connectable.connect() as conn:
        context.configure(
            connection=conn,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

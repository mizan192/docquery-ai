from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool 
from alembic import context 
import sys 
import os 

# add app directory to sys.path
# sys.path.append(os.getcwd())
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import base 
from app.database import Base
# just import models module
# this triggers __init__.py automatically
import app.models

config = context.config  
fileConfig(config.config_file_name) 

# this tells alembic about your DB tables (sqlalchemy's Base)
target_metadata = Base.metadata 

# Offline mode: Generates raw SQL scripts without connecting to a live database.
# Best for dry-runs (e.g. alembic upgrade head --sql) or generating SQL for DBAs.
def run_migrations_offline() -> None: 
    url = config.get_main_option("sqlalchemy.url")
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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

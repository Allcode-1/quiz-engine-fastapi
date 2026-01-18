import sys
import os
from os.path import abspath, dirname
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context
from dotenv import load_dotenv


load_dotenv()
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from app.db.base import Base
from app.models.user import User 

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = os.getenv("DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    db_url = os.getenv("DATABASE_URL")
    
    # log
    print(f"--- DEBUG: CONNECTING TO {db_url} ---")

    if not db_url:
        raise ValueError("DATABASE_URL is not found in .env!")

    # connect through url
    connectable = create_engine(
        db_url, 
        poolclass=pool.NullPool,
        connect_args={"client_encoding": "utf8"})

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
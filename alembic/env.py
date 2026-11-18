"""
Alembic migration environment.

The database address is NOT written in alembic.ini.
It comes from the DATABASE_URL environment variable (the .env file),
the same place the FastAPI app reads it from.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

import app.models  # noqa: F401  (imports every model, so all tables are known)
from app.database import DATABASE_URL, Base

config = context.config

# Set up logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic compares this metadata (our models) with the database for --autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate SQL without connecting to the database (alembic upgrade head --sql)."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database and apply the migrations."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

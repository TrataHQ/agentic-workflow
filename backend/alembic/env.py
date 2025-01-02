from dotenv import load_dotenv

load_dotenv(".env")

from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlmodel import SQLModel
from alembic import context
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool
from sqlalchemy.engine import engine_from_config

from agentic_workflow.db.models import App, Connection, Workflow, AppAction

import os

load_dotenv(".env")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define the tables you want to track
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def include_object(object, name, type_, reflected, compare_to):
    # Only include tables that are defined in your models
    if type_ == "table":
        return name in target_metadata.tables
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    url = os.getenv(
        "SYNC_PG_DATABASE_URI", "postgresql://root:password@localhost:5432/core_db"
    )
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object,
        dialect_opts={"paramstyle": "named"},
        version_table="workflows_alembic_version",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # Add this configuration
    config.set_main_option("version_table", "workflows_alembic_version")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=NullPool,
    )

    url = os.getenv(
        "SYNC_PG_DATABASE_URI", "postgresql://root:password@localhost:5432/core_db"
    )
    connectable = create_engine(url)

    with connectable.connect() as connection:
        connection.dialect
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            version_table="workflows_alembic_version",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

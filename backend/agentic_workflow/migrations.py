def run_migrations(database_url):
    from alembic.config import Config
    from alembic import command
    import os
    import importlib.resources as pkg_resources
    import sys

    # Get the package root directory (where alembic folder is)
    if hasattr(sys, "_MEIPASS"):  # type: ignore # Handle PyInstaller case
        package_root = sys._MEIPASS  # type: ignore
    else:
        package_root = os.path.dirname(os.path.dirname(__file__))

    alembic_dir = os.path.join(package_root, "alembic")
    alembic_ini = os.path.join(package_root, "alembic.ini")

    # Use the packaged alembic.ini file
    alembic_cfg = Config(alembic_ini)
    alembic_cfg.set_main_option("script_location", alembic_dir)
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    run_migrations("postgresql://postgres:sheik_123@localhost:5432/core_db")

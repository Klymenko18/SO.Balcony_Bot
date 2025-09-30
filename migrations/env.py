from __future__ import annotations
import os
import importlib
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- DATABASE_URL з env ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL не встановлено. Приклад:\n"
        "postgresql+psycopg://balcony:balcony@postgres:5432/balcony"
    )
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# --- де взяти metadata (шлях у .env) ---
tm_path = os.getenv("ALEMBIC_TARGET_METADATA")  # напр.: bot.db.database:Base
if not tm_path or ":" not in tm_path:
    raise RuntimeError(
        "ALEMBIC_TARGET_METADATA має бути у форматі 'module.path:Attribute'. "
        "Приклад: ALEMBIC_TARGET_METADATA=bot.db.database:Base"
    )
mod_path, attr_name = tm_path.split(":", 1)
module = importlib.import_module(mod_path)
attr = getattr(module, attr_name)

# ✅ Підтримка Base/SQLModel/metadata
target_metadata = getattr(attr, "metadata", attr)

# ⚠️ Дуже важливо: імпортуємо моделі, щоб вони зареєструвались у Base.metadata
# (і autogenerate бачив таблиці)
try:
    import bot.db.models  # noqa: F401
except Exception as e:
    # Не валимо процес, але підкажемо у лог
    print("WARNING: cannot import bot.db.models:", e)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

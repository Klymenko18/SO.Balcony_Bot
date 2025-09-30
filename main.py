import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from bot.handlers.calculator import router as calc_router
from bot.handlers.menu import router as menu_router   # ⬅️ додано
from bot.db.database import get_engine, Base

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it to .env")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())

# порядок має значення: спочатку наш "меню", потім калькулятор
dp.include_router(menu_router)   # ⬅️ додано
dp.include_router(calc_router)


async def prepare_database() -> None:
    """
    Чекаємо готовність Postgres і створюємо таблиці.
    Engine у нас синхронний → виконуємо в окремому треді.
    """
    engine = get_engine()

    async def _retry_create_all():
        from sqlalchemy import text
        for attempt in range(1, 31):  # ~15 c
            try:
                def _ensure():
                    with engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    Base.metadata.create_all(bind=engine)
                await asyncio.to_thread(_ensure)
                logging.info("Database is ready (tables ensured).")
                return
            except Exception as e:
                logging.warning("DB not ready, retry %s/30: %s", attempt, e)
                await asyncio.sleep(0.5)
        raise RuntimeError("Database connection failed after retries")

    await _retry_create_all()


async def main() -> None:
    logging.info("Starting balcony_bot")

    await bot.delete_webhook(drop_pending_updates=True)

    # показати команди у меню Telegram (буде /start і /menu)
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description="Spustiť kalkulačku"),
            BotCommand(command="menu",  description="Zobraziť tlačidlo /start"),
        ])
    except Exception:
        pass

    await prepare_database()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")

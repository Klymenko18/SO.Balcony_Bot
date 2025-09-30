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
dp.include_router(calc_router)


async def prepare_database() -> None:
    """Чекаємо готовність Postgres і створюємо таблиці."""
    engine = get_engine()
    for attempt in range(1, 31):  # ~15 c
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logging.info("Database is ready (tables ensured).")
            return
        except Exception as e:
            logging.warning("DB not ready, retry %s/30: %s", attempt, e)
            await asyncio.sleep(0.5)
    raise RuntimeError("Database connection failed after retries")


async def main() -> None:
    logging.info("Starting balcony_bot")

    # важливо: вимикаємо webhook, щоб працював polling
    await bot.delete_webhook(drop_pending_updates=True)

    # команда в меню
    try:
        await bot.set_my_commands([BotCommand(command="start", description="Spustiť kalkulačku")])
    except Exception:
        pass

    await prepare_database()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")

# bot/handlers/menu.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards.main import start_kb

router = Router(name="menu")

@router.message(Command("menu"))
async def show_menu(message: Message):
    await message.answer(
        "Меню відкрито. Натисни кнопку /start, щоб перезапустити калькулятор.",
        reply_markup=start_kb(),
    )

# опціонально: якщо хтось напише просто "menu" або "меню"
@router.message(F.text.lower().in_({"menu", "меню"}))
async def show_menu_text(message: Message):
    await show_menu(message)

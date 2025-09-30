from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start_kb() -> ReplyKeyboardMarkup:
    """
    Постійна reply-клавіатура з однією кнопкою '/start'.
    Коли юзер її натискає — Telegram відправляє текст '/start',
    і спрацьовує твій існуючий хендлер /start.
    """
    kb = ReplyKeyboardBuilder()
    kb.button(text="/start")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=False)

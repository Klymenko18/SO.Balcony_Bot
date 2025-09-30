from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def yes_no_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Áno", callback_data="confirm_yes"),
         InlineKeyboardButton(text="Nie", callback_data="confirm_no")]
    ])

def contact_methods_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Hovor", callback_data="m_call")],
        [InlineKeyboardButton(text="📱 WhatsApp", callback_data="m_whatsapp")],
        [InlineKeyboardButton(text="💬 Telegram", callback_data="m_telegram")],
        [InlineKeyboardButton(text="↩️ Späť", callback_data="go_back_result")]
    ])

def share_phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📲 Zdieľať číslo", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )

def remove_reply_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()

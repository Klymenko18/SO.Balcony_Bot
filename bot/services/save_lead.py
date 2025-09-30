# bot/services/save_lead.py
from __future__ import annotations
import asyncio
from decimal import Decimal
from typing import Any, Dict
from aiogram.types import Message

from bot.db.database import get_session
from bot.db.crud import create_lead


async def save_lead_from_state(message: Message, data: Dict[str, Any]):
    """
    Викликаєш у фінальному хендлері вашого сценарію (перед 'Ďakujeme!...').
    Виконує синхронний запис у БД у треді, щоб не блокувати loop.
    """
    def _do():
        db = get_session()
        try:
            return create_lead(
                db,
                tg_user_id=message.from_user.id,
                tg_username=message.from_user.username,
                length_m=Decimal(str(data["length_m"])),
                width_m=Decimal(str(data["width_m"])),
                area_m2=Decimal(str(data["area_m2"])),
                price_eur=Decimal(str(data["price_eur"])),
                contact_method=data.get("contact_method"),
                contact_phone=data.get("contact_phone"),
                contact_name=data.get("contact_name"),
                prefer_time=data.get("prefer_time"),
                comment=data.get("comment"),
                contact_text=data.get("contact_text"),
            )
        finally:
            db.close()

    return await asyncio.to_thread(_do)

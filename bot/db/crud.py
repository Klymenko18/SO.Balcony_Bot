from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Lead

async def create_lead(
    session: AsyncSession,
    *,
    tg_user_id: int,
    tg_username: str | None,
    length_m: Decimal,
    width_m: Decimal,
    area_m2: Decimal,
    price_eur: Decimal,
    contact_text: str | None = None,
    contact_method: str | None = None,
    contact_phone: str | None = None,
    contact_name: str | None = None,
    prefer_time: str | None = None,
    comment: str | None = None,
) -> Lead:
    lead = Lead(
        tg_user_id=tg_user_id,
        tg_username=tg_username,
        length_m=length_m,
        width_m=width_m,
        area_m2=area_m2,
        price_eur=price_eur,
        contact_text=contact_text,
        contact_method=contact_method,
        contact_phone=contact_phone,
        contact_name=contact_name,
        prefer_time=prefer_time,
        comment=comment,
    )
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    return lead

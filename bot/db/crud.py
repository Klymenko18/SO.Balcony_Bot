from __future__ import annotations
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Lead


def _norm_phone(p: Optional[str]) -> Optional[str]:
    if not p:
        return p
    p = p.strip()
    if p and p[0].isdigit():
        p = "+" + p
    return p


def create_lead(
    db: Session,
    *,
    tg_user_id: int,
    tg_username: Optional[str],
    length_m: Decimal,
    width_m: Decimal,
    area_m2: Decimal,
    price_eur: Decimal,
    contact_method: Optional[str],
    contact_phone: Optional[str],
    contact_name: Optional[str],
    prefer_time: Optional[str],
    comment: Optional[str],
    contact_text: Optional[str] = None,
):
    if comment and comment.strip() in {"-", "—", "_", ""}:
        comment = None
    contact_phone = _norm_phone(contact_phone)

    lead = Lead(
        tg_user_id=tg_user_id,
        tg_username=tg_username,
        length_m=length_m,
        width_m=width_m,
        area_m2=area_m2,
        price_eur=price_eur,
        contact_method=contact_method,
        contact_phone=contact_phone,
        contact_name=contact_name,
        prefer_time=prefer_time,
        comment=comment,
        contact_text=contact_text,
    )
    db.add(lead)
    db.commit()       # ✅ обовʼязково
    db.refresh(lead)
    return lead


def latest_leads(db: Session, n: int = 5):
    res = db.execute(select(Lead).order_by(Lead.id.desc()).limit(n))
    return list(res.scalars())


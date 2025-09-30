from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Numeric, String, DateTime
from .database import Base

class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    tg_username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    length_m: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    width_m:  Mapped[Decimal] = mapped_column(Numeric(10, 4))
    area_m2:  Mapped[Decimal] = mapped_column(Numeric(12, 4))
    price_eur: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    # ✅ Struktúrované pole
    contact_method: Mapped[str | None] = mapped_column(String(20), nullable=True)    # 'call' | 'whatsapp' | 'telegram'
    contact_phone:  Mapped[str | None] = mapped_column(String(32), nullable=True)
    contact_name:   Mapped[str | None] = mapped_column(String(255), nullable=True)
    prefer_time:    Mapped[str | None] = mapped_column(String(64), nullable=True)    # napr. "10:00–12:00"
    comment:        Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # legacy text (залишимо, щоб нічого не втратити)
    contact_text: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

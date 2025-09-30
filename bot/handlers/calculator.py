import os
import re
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from ..states.calc_state import CalcState
from ..services.calculator import compute_area, compute_price, format_eur, _to_decimal
from ..keyboards.common import yes_no_kb, contact_methods_kb, share_phone_kb, remove_reply_kb

from ..db.database import SessionLocal
from ..db.crud import create_lead

router = Router()
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

WELCOME = (
    "Vitaj v kalkulačke balkónov 🏠\n"
    "Poďme vypočítať orientačnú cenu za PVC (206,5 €/m²).\n\n"
    "<b>Zadaj prosím dĺžku balkóna</b> v metroch (napr. 3 alebo 2,7)."
)
ASK_WIDTH = "Super 👍\nTeraz <b>zadaj šírku balkóna</b> v metroch (napr. 1,5)."
BAD_NUMBER = (
    "Vyzerá to, že hodnota nie je číslo. Skús prosím znova.\n"
    "Podporujem aj čiarku: napr. 2,5"
)
RESULT_TEMPLATE = (
    "📏 <b>Balkón</b>: {length} × {width} m = <b>{area} m²</b>\n"
    "💰 <b>Cena</b> (PVC 206,5 €/m²): <b>{price}</b>\n\n"
    "Chceš, aby sa s tebou spojil náš manažér?"
)

CONTACT_METHOD_ASK = (
    "Ako ťa máme kontaktovať?\n"
    "Vyber jednu možnosť:"
)

ASK_PHONE_TEXT = (
    "Prosím pošli <b>telefónne číslo</b> (s predvoľbou, napr. +421900123456)\n"
    "alebo použi tlačidlo <b>„📲 Zdieľať číslo“</b>."
)

ASK_NAME_TEXT = "Ďakujem! Ako ťa máme osloviť? <b>Meno a priezvisko</b> (alebo len meno)."
ASK_PREFER_TIME_TEXT = "Kedy ti vyhovuje kontakt? (napr. <i>10:00–12:00</i>) — môžeš aj preskočiť odoslaním „-”."
ASK_COMMENT_TEXT = "Poznámka pre nás? (voliteľné, alebo „-” na preskočenie)"

SAVED_TEXT = "Ďakujeme! 📩 Tvoj dopyt sme zaznamenali. Ozveme sa ti čo najskôr."


def _is_number(s: str) -> bool:
    s = s.strip().replace(",", ".")
    try:
        float(s)
        return True
    except ValueError:
        return False


def _normalize_phone(s: str) -> str | None:
    s = s.strip()
    s = s.replace(" ", "").replace("-", "")
    if not s:
        return None
    # povoliť + a číslice
    if re.fullmatch(r"\+?\d{7,15}", s):
        # ak nezačína +, pridáme lokálnu predvoľbu? necháme tak – používateľ pošle celé
        return s if s.startswith("+") else "+" + s
    return None


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME)
    await state.set_state(CalcState.DLZKA)


@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Začnime odznova. " + WELCOME)
    await state.set_state(CalcState.DLZKA)


@router.message(CalcState.DLZKA, F.text)
async def ask_width(message: Message, state: FSMContext):
    text = message.text.strip()
    # "3x1.5" skratka
    for sep in ("x", "X", "*"):
        if sep in text:
            parts = text.replace(",", ".").split(sep, maxsplit=1)
            if len(parts) == 2:
                l, w = [t.strip() for t in parts]
                if _is_number(l) and _is_number(w):
                    await state.update_data(length=l, width=w)
                    return await show_result(message, state)
            break
    if not _is_number(text):
        return await message.answer(BAD_NUMBER)

    await state.update_data(length=text)
    await message.answer(ASK_WIDTH)
    await state.set_state(CalcState.SIRKA)


@router.message(CalcState.SIRKA, F.text)
async def compute_and_show(message: Message, state: FSMContext):
    text = message.text.strip()
    if not _is_number(text):
        return await message.answer(BAD_NUMBER)
    await state.update_data(width=text)
    await show_result(message, state)


async def show_result(message: Message, state: FSMContext):
    data = await state.get_data()
    length_raw = str(data.get("length"))
    width_raw = str(data.get("width"))

    area = compute_area(length_raw, width_raw)
    price = compute_price(area)

    length = length_raw.replace(".", ",")
    width = width_raw.replace(".", ",")
    area_str = f"{area:.2f}".replace(".", ",")

    await message.answer(
        RESULT_TEMPLATE.format(
            length=length, width=width, area=area_str, price=format_eur(price)
        ),
        reply_markup=yes_no_kb()
    )
    await state.update_data(area=str(area), price=str(price))
    await state.set_state(CalcState.SHOW_RESULT)


@router.callback_query(CalcState.SHOW_RESULT, F.data == "confirm_yes")
async def confirm_yes(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer(CONTACT_METHOD_ASK, reply_markup=contact_methods_kb())
    await state.set_state(CalcState.PICK_METHOD)


@router.callback_query(CalcState.SHOW_RESULT, F.data == "confirm_no")
async def confirm_no(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await cb.message.answer("OK 👍 Kedykoľvek napíš /start a môžeme prepočítať znova.")


@router.callback_query(CalcState.PICK_METHOD, F.data.in_({"m_call", "m_whatsapp", "m_telegram"}))
async def pick_method(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    m = cb.data
    method_map = {"m_call": "call", "m_whatsapp": "whatsapp", "m_telegram": "telegram"}
    await state.update_data(contact_method=method_map[m])
    await cb.message.answer(ASK_PHONE_TEXT, reply_markup=share_phone_kb())
    await state.set_state(CalcState.ASK_PHONE)


@router.callback_query(CalcState.PICK_METHOD, F.data == "go_back_result")
async def back_to_result(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    # просто запропонуємо /reset
    await cb.message.answer("Môžeme začať znova. Napíš /reset.")


@router.message(CalcState.ASK_PHONE, F.contact)
async def got_contact_share(message: Message, state: FSMContext):
    phone = _normalize_phone("+" + str(message.contact.phone_number).lstrip("+"))
    if not phone:
        return await message.answer("Číslo sa nepodarilo prečítať. Zadaj prosím manuálne vo formáte +4219xxxxxx.")
    await state.update_data(contact_phone=phone)
    await message.answer(ASK_NAME_TEXT, reply_markup=remove_reply_kb())
    await state.set_state(CalcState.ASK_NAME)


@router.message(CalcState.ASK_PHONE, F.text)
async def got_phone_text(message: Message, state: FSMContext):
    phone = _normalize_phone(message.text)
    if not phone:
        return await message.answer("Formát čísla nesedí. Skús ešte raz, napr. +421900123456.")
    await state.update_data(contact_phone=phone)
    await message.answer(ASK_NAME_TEXT, reply_markup=remove_reply_kb())
    await state.set_state(CalcState.ASK_NAME)


@router.message(CalcState.ASK_NAME, F.text)
async def got_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        return await message.answer("Prosím uveď meno (aspoň 2 znaky).")
    await state.update_data(contact_name=name)
    await message.answer(ASK_PREFER_TIME_TEXT)
    await state.set_state(CalcState.ASK_PREFER_TIME)


@router.message(CalcState.ASK_PREFER_TIME, F.text)
async def got_prefer_time(message: Message, state: FSMContext):
    prefer = None if message.text.strip() == "-" else message.text.strip()
    await state.update_data(prefer_time=prefer)
    await message.answer(ASK_COMMENT_TEXT)
    await state.set_state(CalcState.ASK_COMMENT)


@router.message(CalcState.ASK_COMMENT, F.text)
async def got_comment_and_save(message: Message, state: FSMContext):
    comment = None if message.text.strip() == "-" else message.text.strip()
    data = await state.get_data()

    length_raw = str(data.get("length"))
    width_raw = str(data.get("width"))
    area = compute_area(length_raw, width_raw)  # перерахунок на всяк
    price = compute_price(area)

    # ✍️ Запис у БД
    if SessionLocal is not None:
        async with SessionLocal() as session:
            await create_lead(
                session,
                tg_user_id=message.from_user.id,
                tg_username=message.from_user.username,
                length_m=_to_decimal(length_raw),
                width_m=_to_decimal(width_raw),
                area_m2=area,
                price_eur=price,
                contact_text=None,
                # nové polia
                contact_method=data.get("contact_method"),
                contact_phone=data.get("contact_phone"),
                contact_name=data.get("contact_name"),
                prefer_time=data.get("prefer_time"),
                comment=comment,
            )

    await message.answer(SAVED_TEXT)
    await state.clear()

    # нотиф адміну
    if ADMIN_CHAT_ID:
        admin_payload = (
            "🆕 <b>Nový dopyt z kalkulačky</b>\n"
            f"👤 Meno: {data.get('contact_name')}\n"
            f"📞 Kontakt: {data.get('contact_phone')} ({data.get('contact_method')})\n"
            f"🕒 Preferovaný čas: {data.get('prefer_time') or '–'}\n"
            f"📝 Poznámka: {comment or '–'}\n\n"
            f"📏 Rozmery: {length_raw} × {width_raw} m (plocha {area:.2f} m²)\n"
            f"💰 Cena (PVC): {format_eur(price)}\n"
            f"💬 Od: @{message.from_user.username or message.from_user.id}"
        )
        try:
            await message.bot.send_message(int(ADMIN_CHAT_ID), admin_payload)
        except Exception:
            pass


# Fallback
@router.message(F.text)
async def fallback_text(message: Message, state: FSMContext):
    cur = await state.get_state()
    if cur is None:
        await message.answer("Napíš prosím /start pre spustenie kalkulačky.")

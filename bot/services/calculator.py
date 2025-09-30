from decimal import Decimal, ROUND_HALF_UP


PVC_PRICE_PER_M2 = Decimal("206.5")  # €/m²


def _to_decimal(v: str) -> Decimal:
    cleaned = v.strip().replace(",", ".")
    return Decimal(cleaned)


def compute_area(length_str: str, width_str: str) -> Decimal:
    length = _to_decimal(length_str)
    width = _to_decimal(width_str)
    area = (length * width).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    return area


def compute_price(area_m2: Decimal) -> Decimal:
    price = (area_m2 * PVC_PRICE_PER_M2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return price


def format_eur(value: Decimal) -> str:
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", " ")
    return f"{s} €"

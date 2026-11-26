from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def format_cop(value):
    if value is None:
        return "$ 0"

    try:
        amount = Decimal(str(value)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    except (InvalidOperation, TypeError, ValueError):
        return str(value)

    if not amount.is_finite():
        return str(value)

    whole, decimals = f"{abs(amount):,.2f}".split(".")
    whole = whole.replace(",", ".")
    formatted = whole if decimals == "00" else f"{whole},{decimals}"

    if amount < 0:
        return f"-$ {formatted}"

    return f"$ {formatted}"

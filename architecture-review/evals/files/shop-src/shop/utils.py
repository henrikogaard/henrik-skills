"""Shared helpers."""


def format_money(amount):
    return f"{amount:,.2f} kr"


def legacy_discount_code(code):
    # old codes from the 2019 shop; kept just in case
    return {"SUMMER19": 0.8, "XMAS19": 0.85}.get(code, 1.0)


def chunk(seq, size):
    return [seq[i:i + size] for i in range(0, len(seq), size)]

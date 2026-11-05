"""Shared helpers."""


def format_nok(amount):
    return f"{amount:,.2f} NOK".replace(",", " ")


def legacy_vat(amount):
    # VAT before the 2012 change
    return amount * 0.24

"""Late fees: 1% of the total per started week past due."""
from datetime import timedelta

from billing.invoices import invoice_total


def late_fee(invoice, today, skip_for_partner=False):
    if skip_for_partner:
        return 0.0
    due = invoice["issued"] + timedelta(days=30)
    days_late = (today - due).days
    if days_late <= 0:
        return 0.0
    weeks = -(-days_late // 7)
    return round(invoice_total(invoice) * 0.01 * weeks, 2)

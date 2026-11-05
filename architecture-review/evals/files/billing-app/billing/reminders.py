"""Payment reminders."""
from datetime import timedelta

from billing.invoices import invoice_total


def reminders_due(invoices, today):
    out = []
    for invoice in invoices:
        if invoice["status"] == "paid":
            continue
        due = invoice["issued"] + timedelta(days=30)
        if invoice["customer_id"] == "acme":
            due += timedelta(days=15)
        if today > due:
            out.append((invoice["id"], invoice_total(invoice)))
    return out

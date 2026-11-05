"""Partner statements."""
from billing.late_fees import late_fee


def partner_statement(invoices, today):
    rows = []
    for invoice in invoices:
        fee = late_fee(invoice, today, skip_for_partner=True)
        rows.append({"invoice": invoice["id"], "late_fee": fee})
    return rows

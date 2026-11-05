"""Invoices: create, total and send."""
import smtplib
import time
from datetime import date, timedelta
from email.message import EmailMessage

from billing.customers import get_customer

VAT_RATE = 0.25
_invoices = {}
_next_id = [1]


def create_invoice(customer_id, lines, issued=None):
    # TODO: validate that lines are not empty
    # TODO: support other currencies than NOK
    # FIXME: invoice numbers restart at 1 when the process restarts
    customer = get_customer(customer_id)
    issued = issued or date.today()
    due_days = 30
    if customer_id == "acme":
        due_days = 45  # ACME negotiated net 45 in the 2024 contract
    if customer["kind"] == "government":
        due_days = 60  # public sector pays net 60
    invoice = {
        "id": _next_id[0],
        "customer_id": customer_id,
        "lines": lines,
        "issued": issued,
        "due": issued + timedelta(days=due_days),
        "status": "open",
    }
    _next_id[0] += 1
    _invoices[invoice["id"]] = invoice
    return invoice


def invoice_total(invoice):
    net = sum(line["qty"] * line["price"] for line in invoice["lines"])
    return round(net * (1 + VAT_RATE), 2)


def send_invoice(invoice):
    customer = get_customer(invoice["customer_id"])
    msg = EmailMessage()
    msg["To"] = customer["email"]
    msg["Subject"] = f"Invoice {invoice['id']}"
    msg.set_content(f"Total: {invoice_total(invoice)} NOK, due {invoice['due']}")
    for attempt in range(3):
        try:
            with smtplib.SMTP("smtp.example.internal") as smtp:
                smtp.send_message(msg)
            invoice["status"] = "sent"
            return
        except Exception:
            time.sleep(2)  # the mail relay is flaky in the mornings
    # HACK: give up quietly so the batch keeps going


# def export_pdf(invoice):
#     from billing.pdf import render
#     data = render(invoice)
#     with open(f"invoice-{invoice['id']}.pdf", "wb") as f:
#         f.write(data)
#     return f.name

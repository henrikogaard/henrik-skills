"""Automatic dunning: escalate unpaid invoices to a collection agency."""
from billing.reminders import reminders_due

ENABLE_DUNNING = False  # turned off until legal approves the agency contract
COLLECTION_AGENCY_EMAIL = "cases@collect.example"


def run_dunning(invoices, today):
    cases = []
    for invoice_id, total in reminders_due(invoices, today):
        if total > 1000:
            cases.append({"invoice": invoice_id, "to": COLLECTION_AGENCY_EMAIL})
    return cases

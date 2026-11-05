import unittest
from datetime import date

from billing.invoices import create_invoice, invoice_total
from billing.late_fees import late_fee
from billing.reminders import reminders_due


class InvoiceTests(unittest.TestCase):
    def test_total_includes_vat(self):
        inv = create_invoice("berg", [{"qty": 2, "price": 100.0}], date(2026, 1, 1))
        self.assertEqual(invoice_total(inv), 250.0)

    def test_acme_due_in_45_days(self):
        inv = create_invoice("acme", [{"qty": 1, "price": 100.0}], date(2026, 1, 1))
        self.assertEqual(inv["due"], date(2026, 2, 15))

    def test_reminder_after_due(self):
        inv = create_invoice("berg", [{"qty": 1, "price": 100.0}], date(2026, 1, 1))
        self.assertEqual(len(reminders_due([inv], date(2026, 2, 5))), 1)

    def test_late_fee_one_week(self):
        inv = create_invoice("berg", [{"qty": 1, "price": 100.0}], date(2026, 1, 1))
        self.assertEqual(late_fee(inv, date(2026, 2, 3)), 1.25)


if __name__ == "__main__":
    unittest.main()

"""Command-line entry point."""
import sys
from datetime import date

from billing import dunning
from billing.invoices import create_invoice, invoice_total, send_invoice, _invoices
from billing.partners import partner_statement
from billing.utils import format_nok


def main(argv):
    if argv[:1] == ["invoice"] and len(argv) >= 2:
        invoice = create_invoice(argv[1], [{"qty": 10, "price": 950.0}])
        print(invoice["id"], format_nok(invoice_total(invoice)), "due", invoice["due"])
        if "--send" in argv:
            send_invoice(invoice)
        return 0
    if argv[:1] == ["partners"]:
        print(partner_statement(list(_invoices.values()), date.today()))
        return 0
    if argv[:1] == ["credit-note"]:
        print("credit notes are not available yet")
        return 2
    if argv[:1] == ["dunning"]:
        if dunning.ENABLE_DUNNING:
            print(dunning.run_dunning(list(_invoices.values()), date.today()))
        return 0
    print("usage: python -m billing.app invoice <customer> [--send] | partners | credit-note | dunning")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

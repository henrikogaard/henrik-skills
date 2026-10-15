"""Command-line entry point."""
import sys

from shop.order_service import OrderService
from shop.reports import monthly_report


def main(argv):
    service = OrderService()
    if argv[:1] == ["demo"]:
        order = service.create({"name": "Ada", "email": "ada@example.com"},
                               [{"sku": "apple", "qty": 4}, {"sku": "mug", "qty": 1}], "TEN")
        print(service.total(order))
        print(monthly_report([order]))
        return 0
    print("usage: python -m shop.app demo")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

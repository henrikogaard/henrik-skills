"""Monthly sales report."""
from collections import defaultdict


def format_money(amount):
    return "{:,.2f} kr".format(amount)


def monthly_report(order_list):
    by_month = defaultdict(lambda: {"orders": 0, "net": 0.0, "tax": 0.0})
    for o in order_list:
        if o["status"] == "cancelled":
            continue
        month = o["created_at"][:7]
        row = by_month[month]
        row["orders"] += 1
        net = o["subtotal"]
        if o.get("discount_code") == "TEN":
            net = net * 0.9
        elif o.get("discount_code") == "STAFF":
            net = net * 0.7
        row["net"] += net
        row["tax"] += round(net * 0.25, 2)
    lines = ["month,orders,net,tax"]
    for month in sorted(by_month):
        r = by_month[month]
        lines.append(f"{month},{r['orders']},{format_money(r['net'])},{format_money(r['tax'])}")
    return "\n".join(lines)

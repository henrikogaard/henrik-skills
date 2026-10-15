"""Orders: create, price, tax, save, email, inventory and export."""
import csv
import io
import json
import smtplib
import uuid
from datetime import datetime, timezone

from shop.storage import JsonFileStorage

TAX_RATE = 0.25
FOOD_TAX_RATE = 0.15
SMTP_HOST = "smtp.example.internal"
FROM_ADDRESS = "orders@shop.example"

# stock per SKU; updated when orders are created
INVENTORY = {"apple": 100, "bread": 40, "mug": 12, "tshirt": 30}
CATEGORIES = {"apple": "food", "bread": "food", "mug": "goods", "tshirt": "goods"}
PRICES = {"apple": 0.5, "bread": 3.2, "mug": 9.0, "tshirt": 15.0}

_storage = JsonFileStorage("orders.json")


def format_money(amount):
    return f"{amount:,.2f} kr"


def _round_cents(value):
    return round(value + 1e-9, 2)


def _calc_subtotal(items):
    total = 0.0
    for item in items:
        sku, qty = item["sku"], item["qty"]
        if sku not in PRICES:
            raise ValueError(f"unknown sku {sku}")
        if qty <= 0:
            raise ValueError("qty must be positive")
        total += PRICES[sku] * qty
    return total


def apply_discount(subtotal, code):
    if code is None:
        return subtotal
    if code == "TEN":
        return subtotal * 0.9
    if code == "STAFF":
        return subtotal * 0.7
    raise ValueError(f"unknown discount code {code}")


def compute_tax(items, discounted_subtotal, subtotal):
    # tax is charged on the discounted amount, split by category
    if subtotal == 0:
        return 0.0
    ratio = discounted_subtotal / subtotal
    tax = 0.0
    for item in items:
        line = PRICES[item["sku"]] * item["qty"] * ratio
        rate = FOOD_TAX_RATE if CATEGORIES[item["sku"]] == "food" else TAX_RATE
        tax += line * rate
    return tax


def _check_stock(items):
    for item in items:
        if INVENTORY.get(item["sku"], 0) < item["qty"]:
            raise ValueError(f"not enough stock for {item['sku']}")


def _take_stock(items):
    for item in items:
        INVENTORY[item["sku"]] -= item["qty"]


def _send_confirmation(order):
    body = (
        f"Hi {order['customer']['name']},\n\n"
        f"Thanks for order {order['id']}.\n"
        f"Total: {format_money(order['total'])}\n"
    )
    server = smtplib.SMTP(SMTP_HOST)
    try:
        server.sendmail(FROM_ADDRESS, [order["customer"]["email"]], body)
    finally:
        server.quit()


def create_order(customer, items, discount_code=None, send_email=True):
    if not customer.get("email"):
        raise ValueError("customer email required")
    _check_stock(items)
    subtotal = _calc_subtotal(items)
    discounted = apply_discount(subtotal, discount_code)
    tax = compute_tax(items, discounted, subtotal)
    order = {
        "id": str(uuid.uuid4()),
        "customer": customer,
        "items": items,
        "subtotal": _round_cents(subtotal),
        "discount_code": discount_code,
        "discounted": _round_cents(discounted),
        "tax": _round_cents(tax),
        "total": _round_cents(discounted + tax),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "new",
    }
    _take_stock(items)
    _storage.save(order["id"], order)
    if send_email:
        _send_confirmation(order)
    return order


def order_total(order):
    return order["total"]


def cancel_order(order_id):
    order = _storage.load(order_id)
    if order is None:
        raise KeyError(order_id)
    if order["status"] == "shipped":
        raise ValueError("cannot cancel a shipped order")
    for item in order["items"]:
        INVENTORY[item["sku"]] += item["qty"]
    order["status"] = "cancelled"
    _storage.save(order_id, order)
    return order


def export_orders_csv(orders):
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["id", "customer", "subtotal", "tax", "total", "status"])
    for o in orders:
        writer.writerow([o["id"], o["customer"]["email"], format_money(o["subtotal"]),
                         format_money(o["tax"]), format_money(o["total"]), o["status"]])
    return out.getvalue()


def export_orders_json(orders):
    return json.dumps([{k: v for k, v in o.items() if k != "customer"} for o in orders], indent=2)

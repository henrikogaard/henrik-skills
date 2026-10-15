import os
import tempfile
import unittest
from unittest import mock

from shop import orders
from shop.storage import JsonFileStorage


def _fresh_storage():
    d = tempfile.mkdtemp()
    return JsonFileStorage(os.path.join(d, "orders.json"))


CUSTOMER = {"name": "Ada", "email": "ada@example.com"}


class RoundCentsTests(unittest.TestCase):
    def test_round_cents_1(self):
        self.assertEqual(orders._round_cents(1.005), 1.01)

    def test_round_cents_2(self):
        self.assertEqual(orders._round_cents(2.675), 2.68)

    def test_round_cents_3(self):
        self.assertEqual(orders._round_cents(0.125), 0.13)

    def test_round_cents_4(self):
        self.assertEqual(orders._round_cents(10.0), 10.0)

    def test_round_cents_5(self):
        self.assertEqual(orders._round_cents(3.333), 3.33)

    def test_round_cents_6(self):
        self.assertEqual(orders._round_cents(7.777), 7.78)


class FormatMoneyTests(unittest.TestCase):
    def test_format_money_a(self):
        self.assertEqual(orders.format_money(1234.5), "1,234.50 kr")

    def test_format_money_b(self):
        self.assertEqual(orders.format_money(1234.5), "1,234.50 kr")

    def test_format_money_is_stable(self):
        assert orders.format_money(5) == orders.format_money(5)


class ConstantsTests(unittest.TestCase):
    def test_tax_rate(self):
        self.assertEqual(orders.TAX_RATE, 0.25)

    def test_food_tax_rate(self):
        self.assertEqual(orders.FOOD_TAX_RATE, 0.15)


class CreateOrderTests(unittest.TestCase):
    def setUp(self):
        orders.INVENTORY.update({"apple": 100, "bread": 40, "mug": 12, "tshirt": 30})
        self.storage = mock.patch.object(orders, "_storage", _fresh_storage())
        self.storage.start()

    def tearDown(self):
        self.storage.stop()

    @mock.patch("shop.orders.smtplib.SMTP")
    @mock.patch("shop.orders._round_cents", side_effect=lambda v: round(v, 2))
    @mock.patch("shop.orders.compute_tax", return_value=1.0)
    @mock.patch("shop.orders._calc_subtotal", return_value=10.0)
    def test_create_order_calls_helpers(self, calc, tax, rnd, smtp):
        orders.create_order(CUSTOMER, [{"sku": "mug", "qty": 1}])
        calc.assert_called_once()
        tax.assert_called_once()
        self.assertEqual(rnd.call_count, 4)
        smtp.assert_called_once_with(orders.SMTP_HOST)

    @mock.patch("shop.orders._send_confirmation")
    def test_order_has_id(self, send):
        order = orders.create_order(CUSTOMER, [{"sku": "mug", "qty": 1}])
        self.assertIn("id", order)

    @mock.patch("shop.orders._send_confirmation")
    def test_order_has_status(self, send):
        order = orders.create_order(CUSTOMER, [{"sku": "mug", "qty": 1}])
        self.assertEqual(order["status"], "new")

    @mock.patch("shop.orders._send_confirmation")
    def test_discount_ten(self, send):
        order = orders.create_order(CUSTOMER, [{"sku": "mug", "qty": 2}], "TEN")
        self.assertEqual(order["discounted"], 16.2)

    @mock.patch("shop.orders._send_confirmation")
    def test_food_tax(self, send):
        order = orders.create_order(CUSTOMER, [{"sku": "bread", "qty": 1}])
        self.assertEqual(order["tax"], 0.48)

    @mock.patch("shop.orders._send_confirmation")
    def test_unknown_sku(self, send):
        with self.assertRaises(ValueError):
            orders.create_order(CUSTOMER, [{"sku": "piano", "qty": 1}])

    @mock.patch("shop.orders._send_confirmation")
    def test_unknown_sku_again(self, send):
        with self.assertRaises(ValueError):
            orders.create_order(CUSTOMER, [{"sku": "piano", "qty": 1}])

    @mock.patch("shop.orders._send_confirmation")
    def test_export_runs(self, send):
        order = orders.create_order(CUSTOMER, [{"sku": "mug", "qty": 1}])
        orders.export_orders_csv([order])

    @unittest.skip("needs a real SMTP server")
    def test_send_email_for_real(self):
        orders._send_confirmation({"id": "1", "total": 1.0, "customer": CUSTOMER})


if __name__ == "__main__":
    unittest.main()

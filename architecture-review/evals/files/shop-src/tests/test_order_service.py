import unittest
from unittest import mock

from shop.order_service import OrderService


class OrderServiceTests(unittest.TestCase):
    @mock.patch("shop.order_service.orders.create_order")
    def test_create_delegates(self, create):
        OrderService().create({"email": "a@b.c"}, [], "TEN")
        create.assert_called_once_with({"email": "a@b.c"}, [], "TEN")

    @mock.patch("shop.order_service.orders.order_total")
    def test_total_delegates(self, total):
        OrderService().total({"total": 1})
        total.assert_called_once_with({"total": 1})

    @mock.patch("shop.order_service.orders.cancel_order")
    def test_cancel_delegates(self, cancel):
        OrderService().cancel("x")
        cancel.assert_called_once_with("x")

    @mock.patch("shop.order_service.orders.export_orders_csv")
    def test_export_csv_delegates(self, export):
        OrderService().export_csv([])
        export.assert_called_once_with([])

    @mock.patch("shop.order_service.orders.export_orders_json")
    def test_export_json_delegates(self, export):
        OrderService().export_json([])
        export.assert_called_once_with([])


if __name__ == "__main__":
    unittest.main()

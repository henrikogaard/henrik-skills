"""Service layer for orders."""
from shop import orders


class OrderService:
    def create(self, customer, items, discount_code=None):
        return orders.create_order(customer, items, discount_code)

    def total(self, order):
        return orders.order_total(order)

    def cancel(self, order_id):
        return orders.cancel_order(order_id)

    def export_csv(self, order_list):
        return orders.export_orders_csv(order_list)

    def export_json(self, order_list):
        return orders.export_orders_json(order_list)

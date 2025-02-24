import pytest
from decimal import Decimal
from orders.models import Order, Dish, OrderItem


@pytest.mark.django_db
class TestOrderModel:
    def test_update_total_price(self, order_with_items):
        assert order_with_items.total_price == Decimal("200.00")

        OrderItem.objects.create(
            order=order_with_items, dish=Dish.objects.first(), quantity=1
        )
        order_with_items.update_total_price()
        assert order_with_items.total_price == Decimal("300.00")

    def test_get_total_items(self, order_with_items):
        assert order_with_items.get_total_items() == 1

        OrderItem.objects.create(
            order=order_with_items, dish=Dish.objects.first(), quantity=1
        )
        assert order_with_items.get_total_items() == 2


@pytest.mark.django_db
class TestOrderItem:
    def test_calculate_price(self, dish):
        order = Order.objects.create(table_number=1)
        item = OrderItem.objects.create(order=order, dish=dish, quantity=3)
        assert item.price == Decimal("300.00")

    def test_auto_update_order_total(self, order_with_items):
        initial_total = order_with_items.total_price

        order_with_items.items.all().delete()
        order_with_items.refresh_from_db()
        assert order_with_items.total_price == Decimal("0.00")

import pytest
from decimal import Decimal
from django.test import Client
from orders.models import Order, Dish, OrderItem


@pytest.fixture
def dish():
    return Dish.objects.create(name="Тестовое блюдо", price=Decimal("100.00"))


@pytest.fixture
def order():
    return Order.objects.create(table_number=1, status="pending")


@pytest.fixture
def order_with_items(order, dish):
    OrderItem.objects.create(order=order, dish=dish, quantity=2)
    order.update_total_price()
    return order


@pytest.fixture
def client():
    return Client()


@pytest.fixture(autouse=True)
def clean_db():
    yield
    Order.objects.all().delete()
    Dish.objects.all().delete()

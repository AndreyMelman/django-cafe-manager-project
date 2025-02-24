import pytest
from decimal import Decimal
from django.urls import reverse
from orders.models import Order


@pytest.mark.django_db
class TestOrderViews:
    def test_order_list(self, client):
        url = reverse("order_list")
        response = client.get(url)
        assert response.status_code == 200

    def test_create_order(self, client, dish):
        url = reverse("add_order")
        data = {
            "table_number": 1,
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-0-dish": dish.id,
            "form-0-quantity": 2,
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.table_number == 1
        assert order.total_price == Decimal("200.00")

    def test_update_status(self, client, order_with_items):
        url = reverse("update_status", args=[order_with_items.id])

        response = client.post(url, {"status": "ready"})
        assert response.status_code == 302
        order_with_items.refresh_from_db()
        assert order_with_items.status == "ready"

    def test_delete_order(self, client, order_with_items):
        url = reverse("delete_order", args=[order_with_items.id])

        response = client.post(url)
        assert response.status_code == 302
        assert not Order.objects.filter(id=order_with_items.id).exists()


@pytest.mark.django_db
class TestOrderAPI:
    def test_order_create_api(self, client, dish):
        url = reverse("order-list")
        data = {
            "table_number": 1,
            "status": "pending",
            "items": [],
        }
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == 201
        assert Order.objects.count() == 1

    def test_update_status_api(self, client, order_with_items):
        url = reverse("order-update-status", args=[order_with_items.id])
        response = client.post(
            url, {"status": "ready"}, content_type="application/json"
        )
        assert response.status_code == 200

    def test_add_items_api(self, client, order, dish):
        url = reverse("order-add-items", args=[order.id])
        data = [{"dish": dish.id, "quantity": 3}]
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == 400

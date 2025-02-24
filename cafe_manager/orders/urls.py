from django.urls import path

from .views import (
    OrderListView,
    OrderCreateView,
    UpdateStatusView,
    DeleteOrderView,
    RevenueView,
)

urlpatterns = [
    path("", OrderListView.as_view(), name="order_list"),
    path("add/", OrderCreateView.as_view(), name="add_order"),
    path("update_status/<int:pk>/", UpdateStatusView.as_view(), name="update_status"),
    path("delete_order/<int:pk>/", DeleteOrderView.as_view(), name="delete_order"),
    path("revenue/", RevenueView.as_view(), name="revenue"),
]

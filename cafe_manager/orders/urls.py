from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import OrderViewSet, DishViewSet
from .views import (
    OrderListView,
    OrderCreateView,
    UpdateStatusView,
    DeleteOrderView,
    RevenueView,
    EditOrderView,
)

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")
router.register("dishes", DishViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("", OrderListView.as_view(), name="order_list"),
    path("add/", OrderCreateView.as_view(), name="add_order"),
    path("update_status/<int:pk>/", UpdateStatusView.as_view(), name="update_status"),
    path("delete_order/<int:pk>/", DeleteOrderView.as_view(), name="delete_order"),
    path("revenue/", RevenueView.as_view(), name="revenue"),
    path("edit/<int:pk>/", EditOrderView.as_view(), name="edit_order"),
]

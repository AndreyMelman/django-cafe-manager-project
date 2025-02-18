from django.contrib import admin

from orders.models import Dish, Order, OrderItem


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
    )
    list_display_links = (
        "id",
        "name",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "table_number",
        "status",
        "total_price",
        "created_at",
        "updated_at",
    )
    list_display_links = (
        "id",
        "table_number",
    )


@admin.register(OrderItem)
class OrdrItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "dish",
        "quantity",
        "price",
    )
    list_display_links = (
        "id",
        "order",
    )

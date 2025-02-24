from typing import Any
from django.db import models
from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from decimal import Decimal


class Dish(models.Model):
    """
    Модель блюда в меню.

    Attributes:
        name (str): Название блюда, уникальное
        price (Decimal): Цена блюда
    """

    class Meta:
        verbose_name = "Dish"

    name = models.CharField(
        max_length=101,
        unique=True,
    )
    price = models.DecimalField(
        max_digits=11,
        decimal_places=2,
    )

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    """
    Модель заказа.
    
    Attributes:
        table_number (int): Номер столика
        status (str): Статус заказа (в ожидании/готово/оплачено)
        total_price (Decimal): Общая стоимость заказа
        created_at (datetime): Время создания заказа
        updated_at (datetime): Время последнего обновления
    """

    class Meta:
        verbose_name = "Order"
        ordering = ("-id",)

    STATUS_CHOICES = [
        ("pending", "В ожидании"),
        ("ready", "Готово"),
        ("paid", "Оплачено"),
    ]

    table_number = models.PositiveIntegerField()
    status = models.CharField(
        max_length=21,
        choices=STATUS_CHOICES,
        default="pending",
    )
    total_price = models.DecimalField(
        max_digits=11,
        decimal_places=2,
        default=0.00,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_total_price(self) -> None:
        """Пересчитывает общую стоимость заказа на основе позиций."""
        self.total_price = self.items.aggregate(
            total=Sum("price")
        )["total"] or Decimal("0.00")
        self.save()

    def get_total_items(self) -> int:
        return self.items.count()

    def get_status_display(self) -> str:
        return dict(self.STATUS_CHOICES)[self.status]

    def __str__(self) -> str:
        return f"Заказ {self.id} - Стол {self.table_number}"


class OrderItem(models.Model):
    """
    Модель позиции в заказе.
    
    Attributes:
        order (Order): Заказ, к которому относится позиция
        dish (Dish): Заказанное блюдо
        quantity (int): Количество
        price (Decimal): Общая стоимость позиции (цена × количество)
    """

    class Meta:
        verbose_name = "Order Item"

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=11,
        decimal_places=2,
        editable=False,
    )

    def calculate_price(self) -> Decimal:
        """Рассчитывает стоимость позиции на основе цены блюда и количества."""
        return self.dish.price * self.quantity

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.price = self.calculate_price()
        super().save(*args, **kwargs)
        self.order.update_total_price()

    def delete(self, *args: Any, **kwargs: Any) -> None:
        super().delete(*args, **kwargs)
        self.order.update_total_price()

    def __str__(self) -> str:
        return f"{self.quantity} × {self.dish.name} (Заказ {self.order.id})"


@receiver([post_save, post_delete], sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    instance.order.update_total_price()

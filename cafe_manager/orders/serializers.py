from rest_framework import serializers
from .models import Order, OrderItem, Dish
from typing import Dict, Any
from decimal import Decimal


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ["id", "name", "price"]

    def validate_price(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше нуля")
        return value


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["dish", "quantity"]

    def validate_quantity(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше нуля")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "dish", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Order.
    
    Fields:
        id (int): ID заказа
        table_number (int): Номер столика
        status (str): Статус заказа
        total_price (Decimal): Общая стоимость
        created_at (datetime): Время создания
        items (List[OrderItem]): Позиции заказа
        total_items (int): Количество позиций
    """

    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "table_number",
            "status",
            "total_price",
            "created_at",
            "items",
            "total_items",
        ]

    def validate_table_number(self, value: int) -> int:
        """
        Проверяет корректность номера столика.
        
        Args:
            value (int): Номер столика
            
        Returns:
            int: Проверенный номер столика
            
        Raises:
            ValidationError: Если номер столика некорректный
        """
        if value <= 0:
            raise serializers.ValidationError("Номер столика должен быть больше нуля")
        return value

    def validate_status(self, value):
        if value not in dict(Order.STATUS_CHOICES):
            raise serializers.ValidationError("Некорректный статус заказа")
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if 'table_number' in data and data['table_number'] > 100:
            raise serializers.ValidationError("Номер столика не может быть больше 100")
        return data

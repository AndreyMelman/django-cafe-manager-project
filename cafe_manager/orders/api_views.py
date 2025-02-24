from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, QuerySet
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from .models import Order, Dish
from .serializers import (
    OrderSerializer,
    DishSerializer,
    OrderItemCreateSerializer
)
from .exceptions import OrderNotFoundError, InvalidOrderStatusError, DishNotFoundError
from typing import Any, Optional
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с заказами через API.
    
    Endpoints:
    - GET /api/orders/ - список заказов
    - POST /api/orders/ - создание заказа
    - GET /api/orders/{id}/ - детали заказа
    - PUT/PATCH /api/orders/{id}/ - обновление заказа
    - DELETE /api/orders/{id}/ - удаление заказа
    - POST /api/orders/{id}/add_items/ - добавление позиций
    - POST /api/orders/{id}/update_status/ - обновление статуса
    - GET /api/orders/statistics/ - статистика по заказам
    """

    serializer_class = OrderSerializer

    def get_queryset(self) -> QuerySet[Order]:
        """Возвращает queryset всех заказов."""
        return Order.objects.all()

    def perform_create(self, serializer: ModelSerializer) -> None:
        serializer.save()

    def retrieve(
        self, 
        request: Request, 
        *args: Any, 
        **kwargs: Any
    ) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self):
        try:
            return super().get_object()
        except ObjectDoesNotExist:
            raise OrderNotFoundError()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": "Ошибка при создании заказа", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise OrderNotFoundError()
        except Exception as e:
            return Response(
                {"error": "Ошибка при удалении заказа", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def add_items(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Добавляет позиции к существующему заказу.
        
        Args:
            request (Request): HTTP запрос с данными позиций
            pk (int, optional): ID заказа
            
        Returns:
            Response: Результат добавления позиций
            
        Raises:
            DishNotFoundError: Если указанное блюдо не найдено
            OrderNotFoundError: Если заказ не найден
        """
        try:
            order = self.get_object()
            serializer = OrderItemCreateSerializer(data=request.data, many=True)
            
            if not serializer.is_valid():
                return Response(
                    {"error": "Некорректные данные", "detail": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Проверяем существование всех блюд
            dish_ids = [item['dish'] for item in serializer.validated_data]
            existing_dishes = Dish.objects.filter(id__in=dish_ids)
            if len(existing_dishes) != len(dish_ids):
                raise DishNotFoundError()

            items = serializer.save(order=order)
            return Response({"status": "items added", "count": len(items)})

        except DishNotFoundError:
            raise
        except Exception as e:
            return Response(
                {"error": "Ошибка при добавлении позиций", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        
        # Проверяем наличие статуса в запросе
        if not new_status:
            return Response(
                {"error": "Статус не указан"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем валидность статуса
        valid_transitions = {
            'pending': ['ready', 'paid'],
            'ready': ['paid'],
            'paid': []
        }
        
        current_status = order.status
        if new_status not in valid_transitions.get(current_status, []):
            return Response(
                {"error": f"Недопустимый переход из '{current_status}' в '{new_status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()
        
        return Response({
            "status": "success",
            "new_status": new_status
        })

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        try:
            total_orders = Order.objects.count()
            total_revenue = (
                Order.objects.filter(status="paid").aggregate(Sum("total_price"))[
                    "total_price__sum"
                ]
                or 0
            )
            orders_by_status = Order.objects.values("status").annotate(count=Count("id"))

            return Response(
                {
                    "total_orders": total_orders,
                    "total_revenue": total_revenue,
                    "orders_by_status": orders_by_status,
                }
            )
        except Exception as e:
            return Response(
                {"error": "Ошибка при получении статистики", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer

    def get_object(self):
        try:
            return super().get_object()
        except ObjectDoesNotExist:
            raise DishNotFoundError()

    @action(detail=False, methods=["get"])
    def popular(self, request):
        try:
            popular_dishes = Dish.objects.annotate(
                order_count=Count("orderitem")
            ).order_by("-order_count")[:5]

            serializer = self.get_serializer(popular_dishes, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "Ошибка при получении популярных блюд", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

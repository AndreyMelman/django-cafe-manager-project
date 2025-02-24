from rest_framework.exceptions import APIException
from rest_framework import status

class OrderError(APIException):
    """Базовое исключение для заказов"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ошибка в заказе"

class EmptyOrderError(OrderError):
    """Ошибка пустого заказа"""
    default_detail = "Заказ не может быть пустым"

class InvalidStatusTransitionError(OrderError):
    """Ошибка при недопустимом переходе статуса"""
    default_detail = "Недопустимый переход статуса"

class PaidOrderModificationError(OrderError):
    """Ошибка при попытке изменения оплаченного заказа"""
    default_detail = "Нельзя изменять оплаченный заказ"

class OrderNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Заказ не найден"

class InvalidOrderStatusError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Некорректный статус заказа"

class DishNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Блюдо не найдено" 
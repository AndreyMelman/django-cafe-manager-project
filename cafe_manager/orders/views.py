from django.contrib import messages
from django.db.models import Sum, QuerySet
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    TemplateView,
    CreateView,
    UpdateView,
    DeleteView,
)
from typing import Dict, Any, Optional
from django.http import HttpResponse, HttpRequest
from django.db.transaction import atomic
from django.forms import BaseForm, ModelForm

from .forms import OrderForm, OrderItemFormSet
from .models import Order, OrderItem

STATUS_PAID: str = "paid"
STATUS_READY: str = "ready"
STATUS_PENDING: str = "pending"

SORT_ASC: str = "asc"
SORT_DESC: str = "desc"

MSG_ORDER_CREATED: str = "Заказ #{} успешно создан!"
MSG_ORDER_UPDATED: str = "Заказ #{} обновлен"
MSG_ORDER_DELETED: str = "Заказ #{} удален"
MSG_ERROR_DELETING: str = "Ошибка при удалении заказа #{}: {}"


class OrderListView(ListView):
    """
    Представление для отображения списка заказов с возможностью фильтрации и сортировки.

    Поддерживает:
    - Фильтрацию по номеру столика
    - Фильтрацию по статусу
    - Сортировку по статусу (asc/desc)
    """

    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self) -> QuerySet[Order]:
        """
        Возвращает отфильтрованный и отсортированный список заказов.

        Returns:
            QuerySet[Order]: Список заказов, соответствующий фильтрам
        """
        queryset = super().get_queryset()

        table_number = self.request.GET.get("table_number")
        status = self.request.GET.get("status")
        sort_status = self.request.GET.get("sort_status", SORT_ASC)

        if table_number:
            queryset = queryset.filter(table_number=table_number)

        if status:
            queryset = queryset.filter(status=status)

        queryset = queryset.order_by("status" if sort_status == SORT_ASC else "-status")

        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["current_table"] = self.request.GET.get("table_number", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["sort_status"] = self.request.GET.get("sort_status", "asc")
        return context


class OrderCreateView(CreateView):
    """
    Представление для создания нового заказа.

    Особенности:
    - Создание заказа с множественными позициями через формсет
    - Валидация наличия хотя бы одной позиции
    - Атомарное создание заказа (транзакция)
    """

    model = Order
    form_class = OrderForm
    template_name = "orders/create_order.html"
    success_url = reverse_lazy("order_list")

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = OrderItemFormSet(self.request.POST)
        else:
            context["formset"] = OrderItemFormSet(queryset=OrderItem.objects.none())
        return context

    @atomic
    def form_valid(self, form: BaseForm) -> HttpResponse:
        """
        Обрабатывает валидную форму создания заказа.

        Args:
            form (BaseForm): Валидная форма заказа

        Returns:
            HttpResponse: Редирект на список заказов при успехе

        Raises:
            Exception: При ошибке создания заказа или его позиций
        """
        try:
            context = self.get_context_data()
            formset = context["formset"]

            if not formset.is_valid():
                messages.error(self.request, "Ошибка в позициях заказа")
                return self.form_invalid(form)

            self.object = form.save()

            order_items = formset.save(commit=False)
            if not order_items:
                messages.error(
                    self.request, "Заказ должен содержать хотя бы одну позицию"
                )
                self.object.delete()
                return self.form_invalid(form)

            for item in order_items:
                item.order = self.object
                item.save()

            messages.success(self.request, MSG_ORDER_CREATED.format(self.object.id))
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Ошибка при создании заказа: {str(e)}")
            return self.form_invalid(form)


class UpdateStatusView(UpdateView):
    """
    Представление для обновления статуса заказа.

    Attributes:
        model: Модель заказа
        fields: Поля для обновления
        template_name: Шаблон формы
        success_url: URL для редиректа после успешного обновления
    """

    model = Order
    fields = ["status"]
    template_name = "orders/update_status.html"
    success_url = reverse_lazy("order_list")

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """
        Обработка валидной формы обновления статуса.

        Args:
            form: Форма с валидными данными

        Returns:
            HttpResponse: Ответ с редиректом
        """
        messages.success(self.request, f"Статус заказа #{self.object.id} обновлен")
        return super().form_valid(form)


class DeleteOrderView(DeleteView):
    """
    Представление для удаления заказа.

    Attributes:
        model: Модель заказа
        success_url: URL для редиректа после успешного удаления
    """

    model = Order
    success_url = reverse_lazy("order_list")

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Удаление заказа с проверкой возможности удаления.

        Args:
            request: HTTP запрос
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы

        Returns:
            HttpResponse: Ответ с редиректом
        """
        order: Order = self.get_object()
        order_id: int = order.id

        try:
            if order.status == STATUS_PAID:
                messages.error(request, f"Нельзя удалить оплаченный заказ #{order_id}")
                return self.get(request, *args, **kwargs)

            response: HttpResponse = super().delete(request, *args, **kwargs)
            messages.success(request, MSG_ORDER_DELETED.format(order_id))
            return response

        except Exception as e:
            messages.error(request, MSG_ERROR_DELETING.format(order_id, str(e)))
            return self.get(request, *args, **kwargs)


class RevenueView(TemplateView):
    """
    Представление для отображения выручки.

    Attributes:
        template_name: Шаблон страницы
    """

    template_name = "orders/revenue.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Получение контекста с данными о выручке.

        Args:
            **kwargs: Дополнительные параметры

        Returns:
            Dict[str, Any]: Контекст шаблона с данными о выручке
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context["total_revenue"] = (
            Order.objects.filter(status=STATUS_PAID).aggregate(
                total=Sum("total_price")
            )["total"]
            or 0
        )
        return context


class EditOrderView(UpdateView):
    model = Order
    fields = ["table_number"]
    template_name = "orders/edit_order.html"
    success_url = reverse_lazy("order_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = OrderItemFormSet(
            queryset=OrderItem.objects.filter(order=self.object)
        )
        return context

    @atomic
    def form_valid(self, form):
        try:
            if self.object.status == STATUS_PAID:
                messages.error(self.request, "Нельзя редактировать оплаченный заказ")
                return self.form_invalid(form)

            formset = OrderItemFormSet(
                self.request.POST, queryset=OrderItem.objects.filter(order=self.object)
            )

            if not formset.is_valid():
                messages.error(self.request, "Ошибка в позициях заказа")
                return self.render_to_response(self.get_context_data(form=form))

            # Проверяем, что заказ не останется пустым
            if not any(not getattr(item, "DELETE", False) for item in formset.forms):
                messages.error(self.request, "Заказ не может быть пустым")
                return self.render_to_response(self.get_context_data(form=form))

            formset.save()
            messages.success(self.request, MSG_ORDER_UPDATED.format(self.object.id))
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Ошибка при обновлении заказа: {str(e)}")
            return self.form_invalid(form)

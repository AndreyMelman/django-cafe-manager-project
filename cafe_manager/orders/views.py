from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    TemplateView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import OrderForm, OrderItemFormSet
from .models import Order, OrderItem, Dish


class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        queryset = super().get_queryset()

        table_number = self.request.GET.get("table_number")
        status = self.request.GET.get("status")
        sort_status = self.request.GET.get("sort_status", "asc")

        if table_number:
            queryset = queryset.filter(table_number=table_number)

        if status:
            queryset = queryset.filter(status=status)

        queryset = queryset.order_by("status" if sort_status == "asc" else "-status")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_table"] = self.request.GET.get("table_number", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["sort_status"] = self.request.GET.get("sort_status", "asc")
        return context


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/create_order.html"
    success_url = reverse_lazy("order_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = OrderItemFormSet(self.request.POST)
        else:
            context["formset"] = OrderItemFormSet(queryset=OrderItem.objects.none())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if formset.is_valid():
            self.object = form.save()

            order_items = formset.save(commit=False)
            for item in order_items:
                item.order = self.object
                item.save()

            messages.success(self.request, f"Заказ #{self.object.id} успешно создан!")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class UpdateStatusView(UpdateView):
    model = Order
    fields = ["status"]

    success_url = reverse_lazy("order_list")

    def form_valid(self, form):
        messages.success(self.request, f"Статус заказа #{self.object.id} обновлен")
        return super().form_valid(form)


class DeleteOrderView(DeleteView):
    model = Order
    success_url = reverse_lazy("order_list")

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        order_id = order.id
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f"Заказ #{order_id} удален")
        except Exception as e:
            messages.error(request, f"Ошибка при удалении заказа #{order_id}: {e}")
            return self.get(request, *args, **kwargs)
        return response


class RevenueView(TemplateView):
    template_name = "orders/revenue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_revenue"] = (
            Order.objects.filter(status="paid").aggregate(total=Sum("total_price"))[
                "total"
            ]
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

    def form_valid(self, form):
        formset = OrderItemFormSet(
            self.request.POST, queryset=OrderItem.objects.filter(order=self.object)
        )
        if formset.is_valid():
            formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

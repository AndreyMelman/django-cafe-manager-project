from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.views import View
from django.views.generic import ListView, TemplateView, CreateView

from .models import Order, OrderItem, Dish


class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        queryset = super().get_queryset()

        table_number = self.request.GET.get("table_number")
        status = self.request.GET.get("status")

        if table_number:
            queryset = queryset.filter(table_number=table_number)

        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_table"] = self.request.GET.get("table_number", "")
        context["current_status"] = self.request.GET.get("status", "")
        return context


class AddOrderCreateView(View):
    def get(self, request):
        dishes = Dish.objects.all()
        return render(request, "orders/add_order.html", {"dishes": dishes})

    def post(self, request):
        try:
            table_number = int(request.POST.get("table_number"))
            order = Order.objects.create(table_number=table_number)

            dishes = request.POST.getlist("dish")
            quantities = request.POST.getlist("quantity")

            for dish_id, quantity in zip(dishes, quantities):
                dish = Dish.objects.get(id=dish_id)
                OrderItem.objects.create(
                    order=order,
                    dish=dish,
                    quantity=int(quantity),
                    price=dish.price * int(quantity),
                )

            messages.success(request, f"Заказ #{order.id} успешно создан!")
            return redirect("order_list")

        except Exception as e:
            messages.error(request, f"Ошибка: {str(e)}")
            return self.get(request)


class UpdateStatusView(View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get("status")

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Статус заказа #{order.id} обновлен")
        else:
            messages.error(request, "Неверный статус")

        return redirect("order_list")


class DeleteOrderView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        return render(request, "orders/confirm_delete.html", {"order": order})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order_id = order.id
        order.delete()
        messages.success(request, f"Заказ #{order_id} удален")
        return redirect("order_list")


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

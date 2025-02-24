from django import forms
from django.forms import modelformset_factory
from typing import Any

from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["table_number"]
        labels = {
            "table_number": "🔢 Номер столика",
        }
        widgets = {
            "table_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "Введите номер стола...",
                },
            )
        }
        error_messages = {
            "table_number": {"required": "Укажите номер стола!"},
        }

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        return cleaned_data


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["dish", "quantity"]
        labels = {
            "dish": "🍲 Блюдо",
            "quantity": "🔢 Количество",
        }
        widgets = {
            "dish": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "Укажите количество",
                },
            ),
        }
        error_messages = {
            "dish": {"required": "Выберете блюдо!"},
            "quantity": {"required": "Укажите количество!"},
        }


OrderItemFormSet = modelformset_factory(
    OrderItem,
    form=OrderItemForm,
    extra=1,
)

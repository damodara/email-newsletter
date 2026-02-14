"""
Формы приложения newsletter: подписка (подписчик) для публичной страницы.
"""

from django import forms

from .models import Subscriber


class SubscriberForm(forms.ModelForm):
    """Форма подписки: имя, фамилия, email (для публичной страницы)."""

    class Meta:
        model = Subscriber
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

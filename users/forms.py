"""
Формы приложения users: регистрация и редактирование профиля (email, аватар, телефон, страна).
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля: email, аватар, телефон, страна, имя, фамилия."""

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "avatar", "phone", "country"]


class UserRegisterForm(UserCreationForm):
    """Форма регистрации: email и пароль; пользователь создаётся с is_active=False до подтверждения email."""

    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def save(self, commit=True):
        """Сохраняет пользователя с username=email и is_active=False до подтверждения email."""
        user = super().save(commit=False)
        user.username = user.email
        user.is_active = False  # до подтверждения email
        if commit:
            user.save()
        return user

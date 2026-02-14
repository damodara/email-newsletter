"""
Регистрация модели User в админке с кастомными полями и полями создания пользователя.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка пользователей: вход по email, отображение и редактирование полей."""

    # Отображаемые поля в списке
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined",
    )

    # Поля для поиска
    search_fields = ("email", "first_name", "last_name")

    # Фильтры справа
    list_filter = ("is_active", "is_staff", "is_superuser", "date_joined")

    # Поля при редактировании
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name")}),
        (
            "Разрешения",
            {
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    # Поля при создании нового пользователя
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    # Сортировка
    ordering = ("email",)

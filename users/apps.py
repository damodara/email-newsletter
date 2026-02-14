"""Конфигурация приложения users (пользователи, аутентификация, менеджеры)."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Приложение пользователей: регистрация, вход, сброс пароля, роли (менеджер)."""

    name = "users"

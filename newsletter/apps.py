"""Конфигурация приложения newsletter (рассылки, сообщения, подписчики)."""

from django.apps import AppConfig


class NewsletterConfig(AppConfig):
    """Приложение рассылок: управление сообщениями, подписчиками и рассылками."""

    name = "newsletter"

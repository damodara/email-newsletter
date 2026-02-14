"""
Модели приложения newsletter: сообщения, подписчики, рассылки и попытки отправки.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Message(models.Model):
    """Шаблон письма: тема и текст. Привязан к владельцу (owner)."""

    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    text = models.TextField(verbose_name="Текст письма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="messages",
        verbose_name="Владелец",
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ("can_view_all_messages", "Менеджер: просмотр всех сообщений"),
        ]

    def __str__(self):
        return self.subject


class Subscriber(models.Model):
    """Получатель рассылки: ФИО, email, комментарий. Привязан к владельцу (owner)."""

    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    surname = models.CharField(
        max_length=100, verbose_name="Отчество", blank=True, null=True
    )
    email = models.EmailField(unique=True, verbose_name="E-mail")
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Дата создания"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subscribers",
        verbose_name="Владелец",
    )

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        db_table = "subscriber"
        ordering = ["-created_at", "email"]
        permissions = [
            ("can_view_all_subscribers", "Менеджер: просмотр всех получателей"),
        ]

    def __str__(self):
        return self.email


class Mailing(models.Model):
    """
    Рассылка: период (start_time, end_time), статус, сообщение, получатели.
    Владелец (owner), флаг отключения менеджером (is_disabled).
    Статус пересчитывается через update_status().
    """

    STATUS_CHOICES = [
        ("created", "Создана"),
        ("running", "Запущена"),
        ("completed", "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(Subscriber, verbose_name="Получатели")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="mailings",
        verbose_name="Владелец",
    )
    is_disabled = models.BooleanField(
        default=False,
        verbose_name="Отключена менеджером",
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("can_view_all_mailings", "Менеджер: просмотр всех рассылок"),
            ("can_disable_mailing", "Менеджер: отключение рассылки"),
        ]

    def clean(self):
        """Валидация: при создании start_time не в прошлом; start_time < end_time."""
        if self.start_time and self.end_time:
            # «Не в прошлом» — только при создании новой рассылки
            if not self.pk and self.start_time < timezone.now():
                raise ValidationError("Дата начала не может быть в прошлом.")
            if self.start_time >= self.end_time:
                raise ValidationError("Дата начала должна быть раньше даты окончания.")

    def save(self, *args, **kwargs):
        """Сохранение с вызовом full_clean(), кроме обновления только status."""
        if "update_fields" in kwargs and kwargs["update_fields"] == ["status"]:
            super().save(*args, **kwargs)
        else:
            self.full_clean()
            super().save(*args, **kwargs)

    def update_status(self):
        """Пересчитывает статус по текущему времени (created/running/completed) и сохраняет при изменении."""
        now = timezone.now()
        new_status = self.status

        if now < self.start_time:
            new_status = "created"
        elif self.start_time <= now <= self.end_time:
            new_status = "running"
        else:
            new_status = "completed"

        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=["status"])

    def __str__(self):
        return f"Рассылка {self.id} — {self.get_status_display()}"


class MessageAttempt(models.Model):
    """Одна попытка отправки письма: время, статус (успех/ошибка), ответ сервера, рассылка, подписчик."""

    STATUS_CHOICES = [
        ("Успешно", "Успешно"),
        ("Не успешно", "Не успешно"),
    ]

    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки",
        null=True,
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус"
    )
    server_response = models.TextField(
        blank=True, null=True, verbose_name="Ответ почтового сервера"
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        verbose_name="Рассылка",
        related_name="attempts",
    )
    subscriber = models.ForeignKey(
        Subscriber, on_delete=models.CASCADE, verbose_name="Подписчик"
    )

    class Meta:
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"
        ordering = ["-attempt_time"]

    def __str__(self):
        return f"{self.mailing} → {self.subscriber.email} ({self.status})"

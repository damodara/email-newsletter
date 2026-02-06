from django.db import models
from django.utils import timezone


class Subscriber(models.Model):
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

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        db_table = "subscriber"
        ordering = ["-created_at", "email"]

    def __str__(self):
        return self.email


class Message(models.Model):
    subject = models.CharField(max_length=150, verbose_name="Тема письма")
    text = models.TextField(verbose_name="Текст письма")
    subscriber = models.ForeignKey(
        Subscriber,
        on_delete=models.SET_NULL,
        verbose_name="Получатель",
        null=True,
        blank=True,
        related_name="messages",
    )
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Письмо"
        verbose_name_plural = "Письма"
        db_table = "message"
        ordering = ["-created_at", "subject"]

    def __str__(self):
        return self.subject

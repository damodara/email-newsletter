from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    text = models.TextField(verbose_name="Текст письма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.subject


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


class Mailing(models.Model):
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

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time < timezone.now():
                raise ValidationError("Дата начала не может быть в прошлом.")
            if self.start_time >= self.end_time:
                raise ValidationError("Дата начала должна быть раньше даты окончания.")

    def save(self, *args, **kwargs):
        if 'update_fields' in kwargs and kwargs['update_fields'] == ['status']:
            super().save(*args, **kwargs)
        else:
            self.full_clean()
            super().save(*args, **kwargs)

    def update_status(self):
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

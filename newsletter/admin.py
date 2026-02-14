"""
Регистрация моделей newsletter в админке: сообщения, подписчики, рассылки, попытки.
Действие «Отправить рассылку сейчас» для рассылок.
"""

from django.conf import settings
from django.contrib import admin, messages
from django.core.mail import send_mail
from django.utils import timezone

from .models import Mailing, Message, MessageAttempt, Subscriber


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Админка для шаблонов писем (сообщений)."""

    list_display = ("subject", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    """Админка для получателей рассылки (подписчиков)."""

    list_display = ("first_name", "last_name", "email", "created_at")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Админка для рассылок; действие «Отправить выбранную рассылку сейчас»."""

    list_display = (
        "__str__",
        "start_time",
        "end_time",
        "status",
        "owner",
        "is_disabled",
        "can_send_now",
        "attempts_count",
    )
    list_filter = ("status", "start_time", "end_time", "is_disabled")
    filter_horizontal = ("recipients",)
    actions = ["send_mailing_now"]

    def can_send_now(self, obj):
        """Проверка: текущее время в интервале [start_time, end_time]."""
        now = timezone.now()
        return obj.start_time <= now <= obj.end_time

    can_send_now.boolean = True
    can_send_now.short_description = "Можно отправлять?"

    def attempts_count(self, obj):
        """Количество попыток отправки по данной рассылке."""
        return obj.attempts.count()

    attempts_count.short_description = "Попыток отправки"

    def send_mailing_now(self, request, queryset):
        """Действие: отправить выбранные рассылки сейчас (если время в интервале и есть получатели)."""
        now = timezone.now()

        for mailing in queryset:
            if not (mailing.start_time <= now <= mailing.end_time):
                self.message_user(
                    request,
                    f"❌ Рассылка '{mailing}' не может быть запущена: "
                    f"текущее время вне интервала ({mailing.start_time} – {mailing.end_time}).",
                    level=messages.ERROR,
                )
                continue

            recipients = mailing.recipients.all()
            if not recipients:
                self.message_user(
                    request,
                    f"🟡 У рассылки '{mailing}' нет получателей.",
                    level=messages.WARNING,
                )
                continue

            successful_sends = 0
            failed_sends = 0

            for subscriber in recipients:
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.text,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[subscriber.email],
                        fail_silently=False,
                    )
                    MessageAttempt.objects.create(
                        mailing=mailing,
                        subscriber=subscriber,
                        status="Успешно",
                        server_response="250 OK",  # Пример успешного SMTP-ответа
                    )
                    successful_sends += 1
                except Exception as e:
                    MessageAttempt.objects.create(
                        mailing=mailing,
                        subscriber=subscriber,
                        status="Не успешно",
                        server_response=str(e),
                    )
                    failed_sends += 1

            self.message_user(
                request,
                f"✅ Рассылка '{mailing}' отправлена: {successful_sends} успешно, {failed_sends} с ошибкой.",
                level=messages.SUCCESS,
            )

    send_mailing_now.short_description = "📨 Отправить выбранную рассылку сейчас"


@admin.register(MessageAttempt)
class MessageAttemptAdmin(admin.ModelAdmin):
    """Админка для попыток отправки писем."""

    list_display = ("mailing", "subscriber", "status", "attempt_time")
    list_filter = ("status", "attempt_time", "mailing")
    readonly_fields = ("attempt_time",)

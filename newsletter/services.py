"""
Логика отправки рассылки: проверка времени, отправка писем, создание попыток.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import MessageAttempt


def run_mailing_now(mailing):
    """
    Запускает рассылку сейчас, если текущее время в [start_time, end_time]
    и рассылка не отключена менеджером. Возвращает (success: bool, message: str).
    """
    now = timezone.now()
    if getattr(mailing, "is_disabled", False):
        return False, "Рассылка отключена менеджером."
    if mailing.start_time > now:
        return False, "Рассылка ещё не началась (текущее время раньше start_time)."
    if mailing.end_time < now:
        return False, "Рассылка уже завершена (текущее время позже end_time)."

    recipients = list(mailing.recipients.all())
    if not recipients:
        return False, "У рассылки нет получателей."

    success_count = 0
    fail_count = 0
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
                server_response="250 OK",
            )
            success_count += 1
        except Exception as e:
            MessageAttempt.objects.create(
                mailing=mailing,
                subscriber=subscriber,
                status="Не успешно",
                server_response=str(e),
            )
            fail_count += 1

    return True, f"Отправлено: {success_count} успешно, {fail_count} с ошибкой."

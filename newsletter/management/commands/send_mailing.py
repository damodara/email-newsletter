"""
Запуск рассылки из командной строки:
  python manage.py send_mailing <mailing_id>
"""

from django.core.management.base import BaseCommand

from newsletter.models import Mailing
from newsletter.services import run_mailing_now


class Command(BaseCommand):
    """Команда: запуск рассылки по ID из командной строки."""

    help = "Запустить рассылку по ID (если текущее время в [start_time, end_time])."

    def add_arguments(self, parser):
        """Добавляет аргумент mailing_id — ID рассылки."""
        parser.add_argument("mailing_id", type=int, help="ID рассылки")

    def handle(self, *args, **options):
        """Выполняет отправку рассылки через run_mailing_now; выводит результат в stdout/stderr."""
        mailing_id = options["mailing_id"]
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(f"Рассылка с ID {mailing_id} не найдена.")
            )
            return
        success, msg = run_mailing_now(mailing)
        if success:
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            self.stderr.write(self.style.ERROR(msg))

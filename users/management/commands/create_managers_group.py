"""
Команда для наполнения базы данных группой «Менеджеры».
Использование: python manage.py create_managers_group
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Создаёт группу «Менеджеры» в БД (если её ещё нет)."""

    help = "Создать группу «Менеджеры» для назначения прав менеджерам сервиса."

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="Менеджеры")
        if created:
            self.stdout.write(self.style.SUCCESS("Группа «Менеджеры» создана."))
        else:
            self.stdout.write("Группа «Менеджеры» уже существует.")

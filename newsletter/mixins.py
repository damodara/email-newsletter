"""
Миксины для ограничения доступа: пользователь — только свои объекты,
менеджер — просмотр всех, без редактирования чужих.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

MANAGER_GROUP_NAME = "Менеджеры"


def is_manager(user):
    """Возвращает True, если пользователь входит в группу «Менеджер»."""
    return user.groups.filter(name=MANAGER_GROUP_NAME).exists()


def get_queryset_for_user(model, user, owner_field="owner"):
    """Queryset: свои объекты для пользователя, все — для менеджера."""
    if is_manager(user):
        return model.objects.all()
    return model.objects.filter(**{owner_field: user})


class OwnerOrManagerMixin(LoginRequiredMixin):
    """Список: свои или все (менеджер). Деталь/изменение/удаление: только свои или менеджер только просмотр."""

    owner_field = "owner"

    def get_queryset(self):
        """Возвращает queryset: свои объекты для пользователя, все — для менеджера."""
        qs = get_queryset_for_user(self.model, self.request.user, self.owner_field)
        return qs

    def get_object(self, queryset=None):
        """Проверяет доступ: менеджер видит всё, пользователь — только свои объекты."""
        obj = super().get_object(queryset)
        if is_manager(self.request.user):
            return obj
        if getattr(obj, self.owner_field, None) != self.request.user:
            raise PermissionDenied("Нет доступа к этому объекту.")
        return obj

    def form_valid(self, form):
        """При создании объекта подставляет request.user в поле owner."""
        if not getattr(form.instance, "pk", None) and hasattr(
            form.instance, self.owner_field
        ):
            setattr(form.instance, self.owner_field, self.request.user)
        return super().form_valid(form)


class OwnerOnlyEditMixin(OwnerOrManagerMixin):
    """Менеджер может только просматривать; редактирование/удаление — только владелец."""

    def get_object(self, queryset=None):
        """Для update/delete запрещает доступ менеджеру и не-владельцу."""
        obj = super().get_object(queryset)
        url_name = self.request.resolver_match.url_name or ""
        if url_name.endswith("_update") or url_name.endswith("_delete"):
            if is_manager(self.request.user):
                raise PermissionDenied(
                    "Менеджер не может редактировать или удалять чужие данные."
                )
            if getattr(obj, self.owner_field, None) != self.request.user:
                raise PermissionDenied("Нет доступа к этому объекту.")
        return obj


class SetOwnerOnCreateMixin(LoginRequiredMixin):
    """При создании объекта подставляет request.user в поле owner."""

    owner_field = "owner"

    def form_valid(self, form):
        """Подставляет request.user в поле owner при создании объекта."""
        if hasattr(form.instance, self.owner_field):
            setattr(form.instance, self.owner_field, self.request.user)
        return super().form_valid(form)

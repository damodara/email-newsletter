"""
Представления приложения users: регистрация с подтверждением email,
вход/выход, сброс пароля, список пользователей и блокировка (для менеджеров).
"""

from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.signing import BadSignature, Signer
from django.shortcuts import get_object_or_404, redirect, render

from newsletter.mixins import is_manager

from .forms import UserProfileForm, UserRegisterForm
from .models import User

CONFIRM_SALT = "email-confirm-key"


def register(request):
    """Регистрация: создание пользователя (is_active=False), отправка письма с ссылкой подтверждения email."""
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Отправка письма с подтверждением email
            signer = Signer(salt=CONFIRM_SALT)
            token = signer.sign(user.pk)
            confirm_url = request.build_absolute_uri(f"/users/confirm-email/{token}/")
            send_mail(
                subject="Подтверждение регистрации",
                message=f"Перейдите по ссылке для подтверждения email:\n{confirm_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            django_messages.success(
                request,
                "Регистрация выполнена. Подтвердите email по ссылке из письма, затем войдите.",
            )
            return redirect("users:login")
    else:
        form = UserRegisterForm()
    return render(request, "registration/register.html", {"form": form})


def confirm_email(request, token):
    """Подтверждение email по ссылке из письма."""
    signer = Signer(salt=CONFIRM_SALT)
    try:
        user_pk = signer.unsign(token)
    except BadSignature:
        django_messages.error(request, "Неверная или устаревшая ссылка подтверждения.")
        return redirect("users:login")
    user = get_object_or_404(User, pk=user_pk)
    user.is_active = True
    user.save(update_fields=["is_active"])
    django_messages.success(request, "Email подтверждён. Теперь вы можете войти.")
    return redirect("users:login")


@login_required
def profile_view(request):
    """Просмотр профиля текущего пользователя."""
    return render(request, "users/profile.html", {"user": request.user})


@login_required
def profile_edit(request):
    """Редактирование профиля текущего пользователя (email, аватар, телефон, страна)."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            django_messages.success(request, "Профиль обновлён.")
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def user_list(request):
    """Список пользователей сервиса (только для менеджеров)."""
    if not is_manager(request.user):
        raise PermissionDenied("Доступ только для менеджеров.")
    users = User.objects.all().order_by("email")
    return render(request, "users/user_list.html", {"users": users})


@login_required
def block_user(request, pk):
    """Блокировка пользователя (только для менеджеров)."""
    if not is_manager(request.user):
        raise PermissionDenied("Доступ только для менеджеров.")
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        django_messages.error(request, "Нельзя заблокировать себя.")
        return redirect("users:user_list")
    user.is_active = False
    user.save()
    django_messages.success(request, f"Пользователь {user.email} заблокирован.")
    return redirect("users:user_list")


@login_required
def unblock_user(request, pk):
    """Разблокировка пользователя (только для менеджеров)."""
    if not is_manager(request.user):
        raise PermissionDenied("Доступ только для менеджеров.")
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.save()
    django_messages.success(request, f"Пользователь {user.email} разблокирован.")
    return redirect("users:user_list")

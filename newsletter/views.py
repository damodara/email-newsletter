"""
Представления приложения newsletter: дашборд, статистика, CRUD подписчиков,
сообщений и рассылок, ручной запуск и отключение рассылок.
"""

from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import SubscriberForm
from .mixins import (
    OwnerOnlyEditMixin,
    OwnerOrManagerMixin,
    SetOwnerOnCreateMixin,
    get_queryset_for_user,
    is_manager,
)
from .models import Mailing, Message, MessageAttempt, Subscriber
from .services import run_mailing_now


@login_required
@vary_on_cookie
@cache_page(60, key_prefix="dashboard")  # кеш 60 сек, разный по пользователю через vary
def dashboard(request):
    """Главная страница: количество рассылок, активных рассылок и уникальных получателей (по владельцу/менеджеру)."""
    now = timezone.now()
    mailings_qs = get_queryset_for_user(Mailing, request.user)
    subscribers_qs = get_queryset_for_user(Subscriber, request.user)
    for m in mailings_qs:
        m.update_status()

    total_mailings = mailings_qs.count()
    active_mailings = mailings_qs.filter(
        start_time__lte=now,
        end_time__gte=now,
        status="running",
    ).count()
    total_subscribers = subscribers_qs.distinct().count()

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "total_subscribers": total_subscribers,
    }

    response = render(request, "dashboard.html", context)
    response["Cache-Control"] = "private, max-age=60"  # клиентское кеширование
    return response


@login_required
def statistics_view(request):
    """Статистика: успешные/неуспешные попытки и количество отправленных сообщений пользователя."""
    if is_manager(request.user):
        attempts_qs = MessageAttempt.objects.all()
    else:
        attempts_qs = MessageAttempt.objects.filter(mailing__owner=request.user)
    total_attempts = attempts_qs.count()
    success_count = attempts_qs.filter(status="Успешно").count()
    fail_count = attempts_qs.filter(status="Не успешно").count()
    context = {
        "total_attempts": total_attempts,
        "success_count": success_count,
        "fail_count": fail_count,
    }
    return render(request, "statistics.html", context)


class IndexView(TemplateView):
    """Публичная страница: список рассылок и форма подписки (если используется)."""

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        """Добавляет в контекст список рассылок и форму подписки."""
        context = super().get_context_data(**kwargs)
        context["mailings"] = Mailing.objects.all().order_by("-start_time")
        context["form"] = SubscriberForm()
        return context

    def post(self, request, *args, **kwargs):
        """Обработка отправки формы подписки."""
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return self.get(request, *args, **kwargs)
        else:
            context = self.get_context_data()
            context["form"] = form
            return self.render_to_response(context)


# === Подписчики ===
class SubscriberListView(OwnerOrManagerMixin, ListView):
    """Список получателей рассылки (свои для пользователя, все для менеджера)."""

    model = Subscriber
    template_name = "subscribers_list.html"
    context_object_name = "object_list"


class SubscriberCreateView(SetOwnerOnCreateMixin, CreateView):
    """Создание получателя рассылки (владелец подставляется автоматически)."""

    model = Subscriber
    fields = ["first_name", "last_name", "surname", "email", "comment"]
    template_name = "subscribers_form.html"
    success_url = reverse_lazy("newsletter:subscriber_list")


class SubscriberUpdateView(OwnerOnlyEditMixin, UpdateView):
    """Редактирование получателя (только владелец)."""

    model = Subscriber
    fields = ["first_name", "last_name", "surname", "email", "comment"]
    template_name = "subscribers_form.html"
    success_url = reverse_lazy("newsletter:subscriber_list")


class SubscriberDeleteView(OwnerOnlyEditMixin, DeleteView):
    """Удаление получателя (только владелец)."""

    model = Subscriber
    template_name = "subscriber_confirm_delete.html"
    success_url = reverse_lazy("newsletter:subscriber_list")


# === Сообщения ===
class MessageListView(OwnerOrManagerMixin, ListView):
    """Список сообщений (шаблонов писем) — свои для пользователя, все для менеджера."""

    model = Message
    template_name = "messages_list.html"
    context_object_name = "object_list"


class MessageCreateView(SetOwnerOnCreateMixin, CreateView):
    """Создание сообщения (шаблона письма). Владелец подставляется автоматически."""

    model = Message
    fields = ["subject", "text"]
    template_name = "message_form.html"
    success_url = reverse_lazy("newsletter:message_list")


class MessageUpdateView(OwnerOnlyEditMixin, UpdateView):
    """Редактирование сообщения (только владелец)."""

    model = Message
    fields = ["subject", "text"]
    template_name = "message_form.html"
    success_url = reverse_lazy("newsletter:message_list")


class MessageDeleteView(OwnerOnlyEditMixin, DeleteView):
    """Удаление сообщения (только владелец)."""

    model = Message
    template_name = "message_confirm_delete.html"
    success_url = reverse_lazy("newsletter:message_list")


# === Рассылки ===
class MailingListView(OwnerOrManagerMixin, ListView):
    """Список рассылок — свои для пользователя, все для менеджера."""

    model = Mailing
    template_name = "mailing_list.html"
    context_object_name = "object_list"


class MailingDetailView(OwnerOrManagerMixin, DetailView):
    """Детальный просмотр рассылки; при открытии пересчитывается статус (update_status)."""

    model = Mailing
    template_name = "mailing_detail.html"

    def get_object(self, queryset=None):
        """При открытии рассылки обновляем её статус по текущему времени."""
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_context_data(self, **kwargs):
        """Добавляет user_is_manager для отображения кнопок менеджера/владельца."""
        context = super().get_context_data(**kwargs)
        context["user_is_manager"] = is_manager(self.request.user)
        return context


@login_required
def disable_mailing_view(request, pk):
    """Отключение рассылки менеджером."""
    if not is_manager(request.user):
        raise PermissionDenied("Доступ только для менеджеров.")
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.is_disabled = True
    mailing.save(update_fields=["is_disabled"])
    django_messages.success(request, f"Рассылка #{pk} отключена.")
    return redirect("newsletter:mailing_detail", pk=pk)


@login_required
def send_mailing_now_view(request, pk):
    """Запуск рассылки вручную (только владелец; если владельца нет — любой авторизованный)."""
    if request.method != "POST":
        return redirect("newsletter:mailing_detail", pk=pk)
    mailing = get_object_or_404(Mailing, pk=pk)
    if is_manager(request.user):
        raise PermissionDenied("Менеджер не может запускать рассылки.")
    owner = getattr(mailing, "owner", None)
    if owner is not None and owner != request.user:
        raise PermissionDenied("Нет доступа к этой рассылке.")
    try:
        success, msg = run_mailing_now(mailing)
        if success:
            django_messages.success(request, msg)
        else:
            django_messages.error(request, msg)
    except Exception as e:
        django_messages.error(
            request,
            f"Ошибка при отправке рассылки: {e}. Проверьте настройки почты в .env (EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD).",
        )
    return redirect("newsletter:mailing_detail", pk=pk)


class MailingCreateView(SetOwnerOnCreateMixin, CreateView):
    """Создание рассылки; сообщение и получатели ограничены своими объектами пользователя."""

    model = Mailing
    fields = ["start_time", "end_time", "message", "recipients"]
    template_name = "mailing_form.html"
    success_url = reverse_lazy("newsletter:mailing_list")

    def get_form(self, form_class=None):
        """Ограничиваем выбор сообщения и получателей только своими объектами (кроме менеджера)."""
        form = super().get_form(form_class)
        if not is_manager(self.request.user):
            form.fields["message"].queryset = Message.objects.filter(
                owner=self.request.user
            )
            form.fields["recipients"].queryset = Subscriber.objects.filter(
                owner=self.request.user
            )
        return form


class MailingUpdateView(OwnerOnlyEditMixin, UpdateView):
    """Редактирование рассылки (только владелец); сообщение и получатели — только свои."""

    model = Mailing
    fields = ["start_time", "end_time", "message", "recipients"]
    template_name = "mailing_form.html"
    success_url = reverse_lazy("newsletter:mailing_list")

    def get_form(self, form_class=None):
        """Ограничиваем выбор сообщения и получателей своими объектами для владельца."""
        form = super().get_form(form_class)
        if (
            not is_manager(self.request.user)
            and form.instance.owner == self.request.user
        ):
            form.fields["message"].queryset = Message.objects.filter(
                owner=self.request.user
            )
            form.fields["recipients"].queryset = Subscriber.objects.filter(
                owner=self.request.user
            )
        return form


class MailingDeleteView(OwnerOnlyEditMixin, DeleteView):
    """Удаление рассылки (только владелец)."""

    model = Mailing
    template_name = "mailing_confirm_delete.html"
    success_url = reverse_lazy("newsletter:mailing_list")

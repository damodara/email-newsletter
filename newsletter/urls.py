"""
Маршруты приложения newsletter: дашборд, статистика, CRUD подписчиков,
сообщений и рассылок, запуск и отключение рассылок.
"""

from django.urls import path

from . import views
from .apps import NewsletterConfig
from .views import (
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingUpdateView,
    MessageCreateView,
    MessageDeleteView,
    MessageListView,
    MessageUpdateView,
    SubscriberCreateView,
    SubscriberDeleteView,
    SubscriberListView,
    SubscriberUpdateView,
)

app_name = NewsletterConfig.name

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("statistics/", views.statistics_view, name="statistics"),
    path("subscribers/", SubscriberListView.as_view(), name="subscriber_list"),
    path(
        "subscribers/create/", SubscriberCreateView.as_view(), name="subscriber_create"
    ),
    path(
        "subscribers/<int:pk>/update/",
        SubscriberUpdateView.as_view(),
        name="subscriber_update",
    ),
    path(
        "subscribers/<int:pk>/delete/",
        SubscriberDeleteView.as_view(),
        name="subscriber_delete",
    ),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path(
        "mailings/<int:pk>/send/", views.send_mailing_now_view, name="mailing_send_now"
    ),
    path(
        "mailings/<int:pk>/disable/", views.disable_mailing_view, name="mailing_disable"
    ),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailings/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"
    ),
    path(
        "mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
]

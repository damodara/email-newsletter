from django.urls import path

from newsletter import views
from newsletter.apps import NewsletterConfig
from newsletter.views import (MailingCreateView, MailingDeleteView,
                              MailingDetailView, MailingListView,
                              MailingUpdateView, MessageCreateView,
                              MessageDeleteView, MessageListView,
                              MessageUpdateView, SubscriberCreateView,
                              SubscriberDeleteView, SubscriberListView,
                              SubscriberUpdateView, IndexView)

app_name = NewsletterConfig.name

urlpatterns = [
    # path("", IndexView.as_view(), name="index"),
    path("", views.dashboard, name="dashboard"),
    # Список получателей
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
    # Список писем
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    # Рассылки
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailings/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"
    ),
    path(
        "mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
]

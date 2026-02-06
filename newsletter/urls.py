from django.urls import path

from newsletter.apps import NewsletterConfig
from newsletter.views import (MessageCreateView, MessageDeleteView,
                              MessageListView, MessageUpdateView,
                              SubscriberCreateView, SubscriberDeleteView,
                              SubscriberListView, SubscriberUpdateView, index)

app_name = NewsletterConfig.name

urlpatterns = [
    path("", index, name="index"),
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
]

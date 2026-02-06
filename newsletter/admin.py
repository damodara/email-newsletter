from django.contrib import admin

from .models import Mailing, Message, Subscriber


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "created_at")
    search_fields = ("subject", "text")


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "start_time",
        "end_time",
        "get_status_display",
        "message",
        "recipients_count",
    )
    list_filter = ("status", "start_time", "end_time")
    filter_horizontal = ("recipients",)

    def recipients_count(self, obj):
        return obj.recipients.count()

    recipients_count.short_description = "Количество получателей"

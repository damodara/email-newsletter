from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from newsletter.models import Message, Subscriber


def index(request):
    letters = Message.objects.all()
    context = {"letters": letters}
    return render(request, "index.html", context)


class SubscriberListView(ListView):
    model = Subscriber
    template_name = "subscribers_list.html"
    context_object_name = "object_list"


class SubscriberCreateView(CreateView):
    model = Subscriber
    fields = ["first_name", "last_name", "surname", "email", "comment"]
    template_name = "subscribers_form.html"
    success_url = reverse_lazy("newsletter:subscriber_list")


class SubscriberUpdateView(UpdateView):
    model = Subscriber
    fields = ["first_name", "last_name", "surname", "email", "comment"]
    template_name = "subscribers_form.html"
    success_url = reverse_lazy("newsletter:subscriber_list")


class SubscriberDeleteView(DeleteView):
    model = Subscriber
    template_name = "subscriber_confirm_delete.html"
    success_url = reverse_lazy("newsletter:subscriber_list")


class MessageListView(ListView):
    model = Message
    template_name = "messages_list.html"
    context_object_name = "object_list"


class MessageCreateView(CreateView):
    model = Message
    fields = ["subject", "text"]
    template_name = "message_form.html"
    success_url = reverse_lazy("newsletter:message_list")


class MessageUpdateView(UpdateView):
    model = Message
    fields = ["subject", "text"]
    template_name = "message_form.html"
    success_url = reverse_lazy("newsletter:message_list")


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "message_confirm_delete.html"
    success_url = reverse_lazy("newsletter:message_list")

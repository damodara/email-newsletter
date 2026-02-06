from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, TemplateView)

from newsletter.forms import SubscriberForm
from newsletter.models import Mailing, Message, Subscriber


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailings'] = Mailing.objects.all().order_by('-start_time')
        context['form'] = SubscriberForm()
        return context

    def post(self, request, *args, **kwargs):
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            # После сохранения — перезагрузим страницу с сообщением (можно добавить success_url)
            return self.get(request, *args, **kwargs)
        else:
            # Если ошибка — вернём форму с ошибками
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)


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


class MailingListView(ListView):
    model = Mailing
    template_name = "mailing_list.html"
    context_object_name = "object_list"


class MailingDetailView(DetailView):
    model = Mailing
    template_name = "mailing_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(CreateView):
    model = Mailing
    fields = ["start_time", "end_time", "message", "recipients"]
    template_name = "mailing_form.html"
    success_url = reverse_lazy("newsletter:mailing_list")


class MailingUpdateView(UpdateView):
    model = Mailing
    fields = ["start_time", "end_time", "message", "recipients"]
    template_name = "mailing_form.html"
    success_url = reverse_lazy("newsletter:mailing_list")


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = "mailing_confirm_delete.html"
    success_url = reverse_lazy("newsletter:mailing_list")

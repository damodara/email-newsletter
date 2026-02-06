from django.shortcuts import render

from newsletter.models import Message


def index(request):
    letters = Message.objects.all()
    context = {"letters": letters}
    return render(request, 'index.html', context)
from django.urls import path
from newsletter.apps import NewsletterConfig
from newsletter.views import index

app_name = NewsletterConfig.name

urlpatterns = [
    path('', index, name='index'),
]

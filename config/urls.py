"""
Главный маршрутизатор проекта: подключает админку, приложения newsletter и users.
"""

from django.contrib import admin
from django.urls import include, path

from newsletter import views as newsletter_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("newsletter/", include("newsletter.urls")),
    path("users/", include("users.urls")),
    path("", newsletter_views.dashboard, name="dashboard"),
]

from django.urls import path

from . import views

app_name = "whatsapp"

urlpatterns = [
    path("upload/", views.upload, name="upload"),
    path("dashboard/", views.dashboard, name="dashboard"),
]

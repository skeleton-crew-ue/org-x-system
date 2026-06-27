from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("compose/", views.broadcast_compose, name="compose"),
    path("history/", views.broadcast_history, name="history"),
]
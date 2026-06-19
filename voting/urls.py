from django.urls import path

from . import views

app_name = "voting"

urlpatterns = [
    path("", views.ballot_list, name="list"),
    path("<int:ballot_id>/", views.ballot_detail, name="detail"),
    path("<int:ballot_id>/cast/", views.cast_vote, name="cast"),
    path("<int:ballot_id>/results/", views.ballot_results, name="results"),
]

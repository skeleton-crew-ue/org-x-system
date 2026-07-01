from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('', views.ballot_list, name='list'),
    path('<int:pk>/', views.ballot_detail, name='detail'),
    path('<int:pk>/vote/', views.cast_vote, name='cast_vote'),
    path('<int:pk>/results/', views.ballot_results, name='results'),
]

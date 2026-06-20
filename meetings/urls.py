from django.urls import path
from . import views

app_name = 'meetings'

urlpatterns = [
    path('', views.meeting_list, name='list'),
    path('<int:pk>/', views.meeting_detail, name='detail'),
    path('<int:pk>/ics/', views.meeting_ics, name='ics'),
]

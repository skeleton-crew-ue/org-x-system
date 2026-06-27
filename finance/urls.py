from django.urls import path
from . import views
app_name = 'finance'
urlpatterns = [
    path('', views.transaction_list, name='list'),
    path('summary/', views.finance_summary, name='summary'),
]

from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Usa las funciones de finance.views, NO meeting_list
    path('', views.transaction_list, name='list'), 
    path('summary/', views.finance_summary, name='summary'),
    path('add/', views.transaction_add, name='add'),
]

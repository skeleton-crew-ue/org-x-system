from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_list, name='list'), 
    
    # Rest of your URLs...
    path('<int:id>/', views.document_detail, name='document_detail'),
    path('<int:id>/download/', views.document_download, name='document_download'),
    path('upload/', views.document_upload, name='document_upload'),
]
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('meetings/', include('meetings.urls')),
    path('finance/', include('finance.urls')), 
]


from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("documents/", include("documents.urls")),
    # --- Module URLs (uncomment as each app gains a urls.py) ---
    path("accounts/", include("members.urls")),
    path("voting/", include("voting.urls")),
    #  path('meetings/', include('meetings.urls')),  
    # path('finance/', include('finance.urls')),
    # path("whatsapp/", include("whatsapp.urls")),     # Lado
]

# Serve uploaded media in local development only. In production WhiteNoise
# handles static; media goes to the Render disk (see docs/Architecture.md §9).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

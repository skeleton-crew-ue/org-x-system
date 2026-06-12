from django.apps import AppConfig


def ready(self):
    import documents.signals
class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'documents'


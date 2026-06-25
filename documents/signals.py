from django.contrib.postgres.search import SearchVector
from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Document


@receiver(post_save, sender=Document)
def update_search_vector(sender, instance, **kwargs):
    if connection.vendor != 'postgresql':
        return

    Document.objects.filter(id=instance.id).update(
        search_vector=SearchVector('title', weight='A') +
                      SearchVector('description', weight='B')
    )

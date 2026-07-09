from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User

GROUP_NAME = "Org Admins"


@receiver(post_save, sender=User)
def sync_org_admins_group(sender, instance, **kwargs):
    group, _ = Group.objects.get_or_create(name=GROUP_NAME)

    if instance.role == User.Role.ADMIN:
        instance.groups.add(group)
        if not instance.is_staff:
            User.objects.filter(pk=instance.pk).update(is_staff=True)
    else:
        instance.groups.remove(group)

from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations

# (app_label, model_name) for every org content model an "Org Admin" should
# fully manage via Django admin. whatsapp.Broadcast is intentionally excluded
# — it's dead code superseded by notifications.Broadcast, the model the real
# broadcast feature (PR #26) actually uses.
CONTENT_MODELS = [
    ("meetings", "meeting"),
    ("voting", "ballot"),
    ("voting", "ballotoption"),
    ("voting", "vote"),
    ("finance", "transaction"),
    ("finance", "category"),
    ("documents", "document"),
    ("documents", "tag"),
    ("whatsapp", "chatexport"),
    ("whatsapp", "chatanalysis"),
    ("notifications", "broadcast"),
]

GROUP_NAME = "Org Admins"


def create_group(apps, schema_editor):
    # On a fresh `migrate`, ContentType/Permission rows for these apps don't
    # exist yet — Django creates them in the post_migrate signal that fires
    # after every migration (including this one) has run. Force creation now
    # instead of racing it, or this silently ships an empty group.
    for app_label in {app_label for app_label, _ in CONTENT_MODELS}:
        create_permissions(
            global_apps.get_app_config(app_label),
            verbosity=0,
            using=schema_editor.connection.alias,
        )

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    User = apps.get_model("members", "User")

    group, _ = Group.objects.get_or_create(name=GROUP_NAME)

    permissions = []
    for app_label, model_name in CONTENT_MODELS:
        ct = ContentType.objects.get(app_label=app_label, model=model_name)
        permissions += list(
            Permission.objects.filter(content_type=ct,
                                       codename__regex=r"^(add|change|delete|view)_")
        )
    group.permissions.set(permissions)

    admins = User.objects.filter(role="ADMIN")
    admins.update(is_staff=True)
    for user in admins:
        user.groups.add(group)


def delete_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0001_initial"),
        ("meetings", "0001_initial"),
        ("voting", "0001_initial"),
        ("finance", "0001_initial"),
        ("documents", "0001_initial"),
        ("whatsapp", "0001_initial"),
        ("notifications", "0001_initial"),
        ("contenttypes", "__first__"),
        ("auth", "__first__"),
    ]

    operations = [
        migrations.RunPython(create_group, delete_group),
    ]

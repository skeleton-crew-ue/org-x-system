from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Broadcast",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("recipient_filter", models.CharField(
                    choices=[("ALL", "All Members"), ("ACTIVE", "Active Members"), ("ADMINS", "Admins Only")],
                    default="ALL",
                    max_length=10,
                )),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
                ("recipient_count", models.PositiveIntegerField(default=0)),
                ("sent_by", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="broadcasts_sent",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["-sent_at"]},
        ),
    ]

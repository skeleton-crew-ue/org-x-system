from django.db import models
from django.conf import settings


class Broadcast(models.Model):
    """Stores every email broadcast sent by an admin."""

    class RecipientFilter(models.TextChoices):
        ALL    = "ALL",    "All Members"
        ACTIVE = "ACTIVE", "Active Members"
        ADMINS = "ADMINS", "Admins Only"

    subject          = models.CharField(max_length=255)
    body             = models.TextField()
    recipient_filter = models.CharField(
        max_length=10,
        choices=RecipientFilter.choices,
        default=RecipientFilter.ALL,
    )
    sent_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="broadcasts_sent",
    )
    sent_at         = models.DateTimeField(auto_now_add=True)
    recipient_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.subject} ({self.sent_at:%Y-%m-%d})"

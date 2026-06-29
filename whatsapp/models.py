from django.conf import settings
from django.db import models

RECIPIENT_FILTER_CHOICES = [
    ("ALL", "All"),
    ("ACTIVE", "Active"),
    ("ADMINS", "Admins"),
]


class ChatExport(models.Model):
    file = models.FileField(upload_to="whatsapp/%Y/%m/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    source_group_name = models.CharField(max_length=200, blank=True)
    message_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.source_group_name or f"Chat export #{self.pk}"


class ChatAnalysis(models.Model):
    chat_export = models.ForeignKey(ChatExport, on_delete=models.CASCADE, related_name="analyses")
    generated_at = models.DateTimeField(auto_now_add=True)
    results = models.JSONField(default=dict)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"Analysis of {self.chat_export} ({self.generated_at:%Y-%m-%d})"


class Broadcast(models.Model):
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    sent_at = models.DateTimeField(auto_now_add=True)
    recipient_filter = models.CharField(max_length=20, choices=RECIPIENT_FILTER_CHOICES)
    recipient_count = models.PositiveIntegerField()

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return self.subject

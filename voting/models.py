from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Ballot(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ballots_created",
    )
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.closes_at and self.opens_at and self.closes_at <= self.opens_at:
            raise ValidationError("closes_at must be after opens_at.")

    def __str__(self):
        return self.title

    def is_open(self):
        now = timezone.now()
        return self.is_active and self.opens_at <= now <= self.closes_at

    def is_closed(self):
        return timezone.now() > self.closes_at


class BallotOption(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=200)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.text


class Vote(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.PROTECT, related_name="votes")
    option = models.ForeignKey(BallotOption, on_delete=models.PROTECT, related_name="votes")
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="votes_cast",
    )
    cast_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("ballot", "voter")

    def __str__(self):
        return f"{self.voter} → {self.ballot}"

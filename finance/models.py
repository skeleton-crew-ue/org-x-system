from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Category(models.Model):
    TYPE_CHOICES = [('INCOME', 'Income'), ('EXPENSE', 'Expense')]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    class Meta:
        unique_together = ("name", "type")

    def __str__(self):
        return f"{self.name} ({self.type})"

class Transaction(models.Model):
    TYPE_CHOICES = [('INCOME', 'Income'), ('EXPENSE', 'Expense')]
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.category and self.category.type != self.type:
            raise ValidationError(f"Category type must be {self.type}")

    def __str__(self):
        return f"{self.type} - {self.amount}"
        
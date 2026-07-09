from django import forms

from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount", "transaction_date", "type", "category", "description"]
        widgets = {
            "transaction_date": forms.DateInput(attrs={"type": "date"}),
        }

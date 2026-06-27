from django import forms
from .models import Broadcast


class BroadcastForm(forms.ModelForm):
    class Meta:
        model  = Broadcast
        fields = ("subject", "recipient_filter", "body")
        widgets = {
            "subject": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Email subject",
            }),
            "recipient_filter": forms.Select(attrs={
                "class": "form-select",
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": "Write your message here…",
            }),
        }

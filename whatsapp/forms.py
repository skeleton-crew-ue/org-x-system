from django import forms

from .models import ChatExport


class ChatExportForm(forms.ModelForm):
    class Meta:
        model = ChatExport
        fields = ["file", "source_group_name"]

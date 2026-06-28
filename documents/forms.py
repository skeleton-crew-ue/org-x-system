# documents/forms.py

from django import forms
from .models import Document, Tag


class DocumentUploadForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Separate tags with commas.",
    )

    class Meta:
        model = Document
        fields = [
            "title",
            "description",
            "file",
            "tags",
        ]

    def clean_tags(self):
        raw = self.cleaned_data.get("tags", "")
        names = [name.strip() for name in raw.split(",") if name.strip()]
        return [Tag.objects.get_or_create(name=name)[0] for name in names]

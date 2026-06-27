from django import forms
from .models import Meeting

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        # Asegúrate de que estos campos existan en tu models.py
        fields = ['title', 'description', 'scheduled_at', 'duration_minutes', 'location_or_link', 'status']
        
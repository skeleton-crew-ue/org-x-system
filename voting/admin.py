from django.contrib import admin
from voting.models import Ballot, BallotOption, Vote # Cambia .models por voting.models

@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    list_display = ('title', 'opens_at', 'closes_at', 'is_active')

admin.site.register(BallotOption)
admin.site.register(Vote)

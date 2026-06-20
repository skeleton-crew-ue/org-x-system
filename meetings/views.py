from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Meeting


@login_required
def meeting_list(request):
    """Display upcoming and past meetings."""
    now = timezone.now()
    upcoming = Meeting.objects.filter(
        scheduled_at__gte=now,
        status='SCHEDULED'
    ).order_by('scheduled_at')
    past = Meeting.objects.filter(
        status='COMPLETED'
    ).order_by('-scheduled_at')
    
    context = {
        'upcoming': upcoming,
        'past': past,
    }
    return render(request, 'meetings/list.html', context)


@login_required
def meeting_detail(request, pk):
    """Display details for a specific meeting."""
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, 'meetings/detail.html', {'meeting': meeting})


@login_required
def meeting_ics(request, pk):
    """Generate and return an ICS calendar file for a meeting."""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Format datetime as YYYYMMDDTHHMMSSZ
    dtstart = meeting.scheduled_at.strftime('%Y%m%dT%H%M%SZ')
    
    # Generate ICS format
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Org X//Meeting//EN
BEGIN:VEVENT
UID:{meeting.pk}@orgx.local
SUMMARY:{meeting.title}
DTSTART:{dtstart}
DESCRIPTION:{meeting.description}
END:VEVENT
END:VCALENDAR"""
    
    response = HttpResponse(ics_content, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="{meeting.title}.ics"'
    return response

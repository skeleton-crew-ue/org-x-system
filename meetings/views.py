from django.shortcuts import render
from .models import Meeting

def meetings_list(request):
    # Traemos todas las reuniones ordenadas por fecha (las más cercanas primero)
    meetings = Meeting.objects.all().order_by('date', 'time')
    
    # Se las pasamos al archivo HTML mediante el contexto
    return render(request, 'meetings/meetings_list.html', {'meetings': meetings})
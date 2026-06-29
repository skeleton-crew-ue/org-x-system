from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.decorators import admin_required

from .analytics import analyze
from .forms import ChatExportForm
from .models import ChatAnalysis, ChatExport


@login_required
@admin_required
def upload(request):
    if request.method == "POST":
        form = ChatExportForm(request.POST, request.FILES)
        if form.is_valid():
            chat_export = form.save(commit=False)
            chat_export.uploaded_by = request.user
            chat_export.save()

            with chat_export.file.open("rb") as f:
                results = analyze(f)

            ChatAnalysis.objects.create(chat_export=chat_export, results=results)
            chat_export.message_count = results["summary"]["total_messages"]
            chat_export.save(update_fields=["message_count"])

            messages.success(request, "Analysis complete.")
            return redirect("whatsapp:dashboard")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ChatExportForm()
    return render(request, "whatsapp/upload.html", {"form": form})


@login_required
def dashboard(request):
    chat_export = ChatExport.objects.first()
    analysis = chat_export.analyses.first() if chat_export else None

    context = {
        "chat_export": chat_export,
        "analysis": analysis,
        "results": analysis.results if analysis else None,
    }
    return render(request, "whatsapp/dashboard.html", context)

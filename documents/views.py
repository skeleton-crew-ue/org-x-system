"""Views for the documents module."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.contrib import messages

from .models import Document
from .forms import DocumentUploadForm
from core.decorators import admin_required


@login_required
def document_list(request):
    q = request.GET.get("q")
    documents = Document.objects.all()
    if q:
        query = SearchQuery(q)
        documents = (
            Document.objects
            .annotate(rank=SearchRank(SearchVector("title", "description"), query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )
    return render(request, "documents/list.html", {
        "documents": documents,
        "query": q
    })


@login_required
def document_detail(request, id):
    doc = get_object_or_404(Document, id=id)
    return render(request, "documents/detail.html", {"document": doc})


@login_required
def document_download(request, id):
    doc = get_object_or_404(Document, id=id)
    return FileResponse(doc.file.open('rb'), as_attachment=True)


@login_required
@admin_required
def document_upload(request):
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)

        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            form.save_m2m()

            messages.success(
                request,
                "Document uploaded successfully."
            )

            return redirect(
                "documents:document_detail",
                id=document.id
            )

        messages.error(
            request,
            "Please correct the errors below."
        )

    else:
        form = DocumentUploadForm()

    return render(
        request,
        "documents/upload.html",
        {"form": form}
    )

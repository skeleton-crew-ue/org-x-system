from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.contrib.postgres.search import SearchQuery

from .models import Document
from core.decorators import admin_required


@login_required
def document_list(request):
    q = request.GET.get("q")

    if q:
        query = SearchQuery(q)
        documents = Document.objects.filter(search_vector=query)
    else:
        documents = Document.objects.all()

    return render(request, "documents/list.html", {"documents": documents})


@login_required
def document_detail(request, id):
    doc = get_object_or_404(Document, id=id)
    return render(request, "documents/detail.html", {"document": doc})


@login_required
def document_download(request, id):
    doc = get_object_or_404(Document, id=id)
    return FileResponse(doc.file.open(), as_attachment=True)


@admin_required
def document_upload(request):
    return render(request, "documents/upload.html")
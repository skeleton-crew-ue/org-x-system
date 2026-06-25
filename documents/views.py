"""Views for the documents module."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse
from django.contrib.postgres.search import SearchRank, SearchQuery
from django.contrib import messages

from .models import Document
from .forms import DocumentUploadForm
from core.decorators import admin_required

DOCUMENTS_PER_PAGE = 20


@login_required
def document_list(request):
    q = request.GET.get("q")
    documents = Document.objects.all()

    if q:
        query = SearchQuery(q)
        documents = (
            documents
            .filter(search_vector=query)
            .annotate(rank=SearchRank("search_vector", query))
            .order_by("-rank")
        )

    paginator = Paginator(documents, DOCUMENTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "documents/list.html", {
        "documents": page_obj,
        "page_obj": page_obj,
        "query": q,
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

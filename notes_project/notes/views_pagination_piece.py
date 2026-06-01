from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Note, Attachment
from .forms import NoteWithAttachmentsForm


def note_list(request):
    query = request.GET.get('q', '')
    per_page = request.GET.get('per_page', 10)  # количество записей на странице, по умолчанию 10
    try:
        per_page = int(per_page)
        if per_page <= 0:
            per_page = 10
    except ValueError:
        per_page = 10

    notes = Note.objects.all()

    if query:
        notes = notes.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    # Пагинация
    paginator = Paginator(notes, per_page)
    page = request.GET.get('page', 1)

    try:
        notes_page = paginator.page(page)
    except PageNotAnInteger:
        notes_page = paginator.page(1)
    except EmptyPage:
        notes_page = paginator.page(paginator.num_pages)

    # ID выбранной заметки для подсветки (опционально)
    selected_note_id = request.GET.get('note_id')

    context = {
        'notes': notes_page,  # объект Page, а не QuerySet
        'search_query': query,
        'selected_note_id': selected_note_id,
        'per_page': per_page,
        'paginator': paginator,
    }
    return render(request, 'notes/note_list.html', context)
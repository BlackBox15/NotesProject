from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from .models import Note, Attachment
from .forms import NoteWithAttachmentsForm


def note_list(request):
    query = request.GET.get('q', '')
    notes = Note.objects.all()

    if query:
        notes = notes.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    context = {
        'notes': notes,
        'search_query': query,
    }
    return render(request, 'notes/note_list.html', context)


def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    context = {'note': note}
    return render(request, 'notes/note_detail.html', context)


def note_create(request):
    if request.method == 'POST':
        form = NoteWithAttachmentsForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save()
            # Обработка загруженных файлов
            files = request.FILES.getlist('attachments')
            for f in files:
                Attachment.objects.create(note=note, file=f)
            messages.success(request, f'Заметка "{note.title}" успешно создана.')
            return redirect(note.get_absolute_url())
    else:
        form = NoteWithAttachmentsForm()

    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Создание заметки'})


def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk)

    if request.method == 'POST':
        form = NoteWithAttachmentsForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            note = form.save()
            # Добавление новых вложений
            files = request.FILES.getlist('attachments')
            for f in files:
                Attachment.objects.create(note=note, file=f)

            # Удаление отмеченных вложений
            delete_attachments = request.POST.getlist('delete_attachments')
            for att_id in delete_attachments:
                try:
                    att = Attachment.objects.get(id=att_id, note=note)
                    att.file.delete()  # удаляем файл с диска
                    att.delete()
                except Attachment.DoesNotExist:
                    pass

            messages.success(request, f'Заметка "{note.title}" успешно обновлена.')
            return redirect(note.get_absolute_url())
    else:
        form = NoteWithAttachmentsForm(instance=note)

    context = {
        'form': form,
        'title': 'Редактирование заметки',
        'note': note,
    }
    return render(request, 'notes/note_form.html', context)


def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        title = note.title
        # Удаляем все файлы вложений
        for att in note.attachments.all():
            att.file.delete()
        note.delete()
        messages.success(request, f'Заметка "{title}" удалена.')
        return redirect('notes:note_list')

    return render(request, 'notes/note_confirm_delete.html', {'note': note})


def attachment_delete(request, pk):
    """Удаление отдельного вложения (AJAX или обычный POST)"""
    attachment = get_object_or_404(Attachment, pk=pk)
    note_pk = attachment.note.pk
    if request.method == 'POST':
        attachment.file.delete()
        attachment.delete()
        messages.success(request, 'Вложение удалено.')
    return redirect('notes:note_update', pk=note_pk)
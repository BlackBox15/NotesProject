import os
import mimetypes
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

class Note(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    tags = TaggableManager(verbose_name='Теги', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('note_detail', args=[str(self.id)])

class Attachment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='attachments', verbose_name='Заметка')
    file = models.FileField(upload_to='notes_attachments/%Y/%m/%d/', verbose_name='Файл')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Загружено')

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'

    def __str__(self):
        return os.path.basename(self.file.name)

    def get_file_type(self):
        """Возвращает тип файла: image, video, audio, other"""
        mime_type, _ = mimetypes.guess_type(self.file.name)
        if mime_type:
            if mime_type.startswith('image/'):
                return 'image'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('audio/'):
                return 'audio'
        return 'other'

    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()
from django.contrib import admin

from apps.files.models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file_type", "content_type", "size", "created_at")
    list_filter = ("file_type", "content_type", "created_at")
    search_fields = ("user__email", "file_url")

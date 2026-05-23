from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models


def upload_to(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f"uploads/{instance.file_type}/{uuid4().hex}{suffix}"


class UploadedFile(models.Model):
    class FileType(models.TextChoices):
        AVATAR = "avatar", "用户头像"
        PET = "pet", "宠物头像"
        MEDICAL = "medical", "就诊记录"
        AI = "ai", "AI 咨询"
        PRODUCT = "product", "商品"
        SERVICE = "service", "服务"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="上传用户",
        related_name="uploaded_files",
        on_delete=models.CASCADE,
    )
    file = models.FileField("文件", upload_to=upload_to)
    file_url = models.CharField("访问 URL", max_length=500, blank=True)
    file_type = models.CharField(
        "文件类型",
        max_length=32,
        choices=FileType.choices,
        default=FileType.PET,
    )
    content_type = models.CharField("MIME 类型", max_length=100)
    size = models.PositiveIntegerField("文件大小")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "上传文件"
        verbose_name_plural = "上传文件"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"], name="files_user_idx"),
            models.Index(fields=["file_type"], name="files_type_idx"),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.file and self.file_url != self.file.url:
            self.file_url = self.file.url
            super().save(update_fields=["file_url"])

    def __str__(self):
        return self.file_url or str(self.file)

from pathlib import Path

from rest_framework import serializers

from apps.files.models import UploadedFile


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024


class UploadedFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    file_type = serializers.ChoiceField(
        choices=UploadedFile.FileType.choices,
        required=False,
        default=UploadedFile.FileType.PET,
    )

    class Meta:
        model = UploadedFile
        fields = ("id", "file", "file_type")

    def validate_file(self, value):
        suffix = Path(value.name).suffix.lower()
        content_type = getattr(value, "content_type", "")
        if suffix not in ALLOWED_IMAGE_EXTENSIONS:
            raise serializers.ValidationError("仅支持 jpg、jpeg、png、webp 图片")
        if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise serializers.ValidationError("文件 MIME 类型不合法")
        if value.size > MAX_UPLOAD_SIZE:
            raise serializers.ValidationError("单文件大小不能超过 5MB")
        return value

    def create(self, validated_data):
        file = validated_data["file"]
        return UploadedFile.objects.create(
            user=self.context["request"].user,
            file=file,
            file_type=validated_data.get("file_type") or UploadedFile.FileType.PET,
            content_type=getattr(file, "content_type", ""),
            size=file.size,
        )

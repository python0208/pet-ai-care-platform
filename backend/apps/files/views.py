from rest_framework import permissions, status
from rest_framework.views import APIView

from apps.common.responses import success_response
from apps.files.serializers import UploadedFileSerializer


class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UploadedFileSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        uploaded_file = serializer.save()
        return success_response(
            {
                "id": uploaded_file.id,
                "url": uploaded_file.file_url,
                "file_type": uploaded_file.file_type,
            },
            status=status.HTTP_201_CREATED,
        )

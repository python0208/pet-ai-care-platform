from django.urls import path

from apps.files.views import FileUploadView

urlpatterns = [
    path("files/upload/", FileUploadView.as_view(), name="files-upload"),
]

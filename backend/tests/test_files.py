from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.files.models import UploadedFile
from apps.users.models import User


class FileUploadApiTests(APITestCase):
    def setUp(self):
        self.temp_media = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.temp_media.name)
        self.override.enable()
        self.user = User.objects.create_user(
            email="file-owner@example.com",
            password="StrongPass123",
        )
        self.url = reverse("files-upload")

    def tearDown(self):
        self.override.disable()
        self.temp_media.cleanup()

    def authenticate(self):
        token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def image_file(self, name="pet.png", size=128, content_type="image/png"):
        return SimpleUploadedFile(name, b"\x89PNG\r\n\x1a\n" + b"0" * size, content_type)

    def test_anonymous_cannot_upload_file(self):
        response = self.client.post(
            self.url,
            {"file": self.image_file(), "file_type": "pet"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_upload_valid_image(self):
        self.authenticate()
        response = self.client.post(
            self.url,
            {"file": self.image_file(), "file_type": "pet"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["code"], 0)
        self.assertIn("/media/uploads/pet/", body["data"]["url"])
        self.assertEqual(body["data"]["file_type"], "pet")
        self.assertEqual(UploadedFile.objects.count(), 1)

    def test_non_image_file_cannot_upload(self):
        self.authenticate()
        text_file = SimpleUploadedFile("note.txt", b"hello", "text/plain")
        response = self.client.post(
            self.url,
            {"file": text_file, "file_type": "pet"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], 40001)

    def test_oversized_file_cannot_upload(self):
        self.authenticate()
        big_file = self.image_file(size=5 * 1024 * 1024 + 1)
        response = self.client.post(
            self.url,
            {"file": big_file, "file_type": "pet"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], 40001)

    def test_upload_success_returns_url(self):
        self.authenticate()
        response = self.client.post(
            self.url,
            {"file": self.image_file("avatar.webp", content_type="image/webp"), "file_type": "pet"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()["data"]
        self.assertIn("url", data)
        self.assertTrue(data["url"].startswith("/media/uploads/pet/"))

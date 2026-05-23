from django.urls import reverse
from rest_framework.test import APITestCase

from apps.users.models import User


class EmailAuthTests(APITestCase):
    def register(self, email="mimi@example.com", password="StrongPass123"):
        return self.client.post(
            reverse("auth-register"),
            {
                "email": email,
                "password": password,
                "confirm_password": password,
                "nickname": "咪咪家长",
            },
            format="json",
        )

    def test_email_register_success(self):
        response = self.register()

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["code"], 0)
        self.assertIn("access_token", body["data"])
        self.assertIn("refresh_token", body["data"])
        self.assertEqual(body["data"]["user"]["email"], "mimi@example.com")

    def test_duplicate_email_cannot_register(self):
        self.register()
        response = self.register()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], 40001)

    def test_password_confirm_mismatch_cannot_register(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "email": "mismatch@example.com",
                "password": "StrongPass123",
                "confirm_password": "OtherPass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_short_password_cannot_register(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "email": "short@example.com",
                "password": "123",
                "confirm_password": "123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_email_password_login_success(self):
        self.register(email="login@example.com")
        response = self.client.post(
            reverse("auth-login"),
            {"email": "login@example.com", "password": "StrongPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("access_token", body["data"])
        self.assertEqual(body["data"]["user"]["email"], "login@example.com")

    def test_wrong_password_cannot_login(self):
        self.register(email="wrong@example.com")
        response = self.client.post(
            reverse("auth-login"),
            {"email": "wrong@example.com", "password": "BadPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_anonymous_cannot_access_me(self):
        response = self.client.get(reverse("users-me"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["code"], 40101)

    def test_authenticated_user_can_access_me(self):
        register_response = self.register(email="me@example.com")
        token = register_response.json()["data"]["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(reverse("users-me"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["email"], "me@example.com")

    def test_user_profile_can_update_allowed_fields(self):
        register_response = self.register(email="profile@example.com")
        token = register_response.json()["data"]["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.put(
            reverse("users-me"),
            {
                "nickname": "新的昵称",
                "avatar": "https://example.com/avatar.png",
                "gender": "female",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["nickname"], "新的昵称")
        self.assertEqual(data["avatar"], "https://example.com/avatar.png")
        self.assertEqual(data["gender"], "female")

    def test_token_refresh_success(self):
        register_response = self.register(email="refresh@example.com")
        refresh = register_response.json()["data"]["refresh_token"]
        response = self.client.post(
            reverse("auth-token-refresh"),
            {"refresh": refresh},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json()["data"])

    def test_sms_and_email_code_endpoints_do_not_exist(self):
        missing_paths = [
            "/api/auth/sms/send/",
            "/api/auth/sms-login/",
            "/api/auth/email/send/",
            "/api/auth/email-login/",
        ]

        for path in missing_paths:
            response = self.client.post(path, {}, format="json")
            self.assertEqual(response.status_code, 404, path)

    def test_user_model_has_no_phone_field(self):
        field_names = {field.name for field in User._meta.fields}

        self.assertNotIn("phone", field_names)

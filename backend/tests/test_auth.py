from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APITestCase

from apps.ai_chat.models import AIActionDraft, AIConversation
from apps.pets.models import Pet
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


class WechatAuthTests(APITestCase):
    @override_settings(DEBUG=True, WECHAT_LOGIN_MOCK_ENABLED=True)
    def test_mock_wechat_login_creates_user(self):
        response = self.client.post(
            reverse("auth-wx-login"),
            {
                "code": "mock-wx-code",
                "platform": "miniapp",
                "nickname": "微信用户",
                "avatar": "",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertTrue(data["is_new_user"])
        self.assertEqual(data["user"]["nickname"], "微信用户")
        self.assertEqual(data["user"]["email"], "")
        self.assertTrue(data["user"]["has_wechat_bound"])
        self.assertNotIn("session_key", data)
        self.assertEqual(User.objects.count(), 1)

    @override_settings(DEBUG=True, WECHAT_LOGIN_MOCK_ENABLED=True)
    def test_same_mock_openid_does_not_create_duplicate_user(self):
        for _ in range(2):
            response = self.client.post(
                reverse("auth-wx-login"),
                {"code": "same-code", "platform": "miniapp"},
                format="json",
            )
            self.assertEqual(response.status_code, 200)

        self.assertEqual(User.objects.count(), 1)
        self.assertFalse(response.json()["data"]["is_new_user"])

    @override_settings(DEBUG=True, WECHAT_LOGIN_MOCK_ENABLED=True)
    def test_authenticated_user_can_bind_wechat_openid(self):
        user = User.objects.create_user(
            email="bind@example.com",
            password="StrongPass123",
            nickname="邮箱用户",
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("auth-wx-login"),
            {"code": "bind-code", "platform": "miniapp"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.wx_openid, "mock_bind-code")
        self.assertFalse(response.json()["data"]["is_new_user"])

    @override_settings(DEBUG=True, WECHAT_LOGIN_MOCK_ENABLED=True)
    def test_one_openid_cannot_bind_multiple_users(self):
        User.objects.create_user(
            email="wechat@example.com",
            password="StrongPass123",
            wx_openid="mock_taken-code",
        )
        user = User.objects.create_user(
            email="other@example.com",
            password="StrongPass123",
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("auth-wx-login"),
            {"code": "taken-code", "platform": "miniapp"},
            format="json",
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["message"], "该微信已绑定其他账号")

    @override_settings(
        DEBUG=True,
        WECHAT_LOGIN_MOCK_ENABLED=False,
        WECHAT_MINI_APPID="",
        WECHAT_MINI_SECRET="",
    )
    def test_missing_wechat_config_without_mock_returns_friendly_error(self):
        response = self.client.post(
            reverse("auth-wx-login"),
            {"code": "no-config", "platform": "miniapp"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "微信小程序登录未配置")

    @override_settings(DEBUG=True, WECHAT_LOGIN_MOCK_ENABLED=True)
    def test_app_platform_returns_reserved_message(self):
        response = self.client.post(
            reverse("auth-wx-login"),
            {"code": "app-code", "platform": "app"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "App 微信登录暂未配置")

    def test_users_me_summary_counts_only_current_user(self):
        user = User.objects.create_user(
            email="summary@example.com",
            password="StrongPass123",
            wx_openid="mock_summary",
        )
        other = User.objects.create_user(
            email="other-summary@example.com",
            password="StrongPass123",
        )
        pet = Pet.objects.create(owner=user, name="豆豆")
        other_pet = Pet.objects.create(owner=other, name="别人家的猫")
        conversation = AIConversation.objects.create(
            user=user,
            pet=pet,
            title="咨询",
        )
        AIConversation.objects.create(user=other, pet=other_pet, title="其他咨询")
        AIActionDraft.objects.create(
            user=user,
            pet=pet,
            conversation=conversation,
            action_type=AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
            display_title="建议添加体重记录",
            confirm_text="是否保存？",
            payload={"pet_id": pet.id},
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("users-me-summary"))

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["pet_count"], 1)
        self.assertEqual(data["ai_conversation_count"], 1)
        self.assertEqual(data["pending_action_count"], 1)
        self.assertTrue(data["has_wechat_bound"])

from datetime import date
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.ai_chat.models import AIConsultationResult, AIConversation, AIMessage
from apps.ai_chat.providers.base import AIConfigurationError, AIProviderError
from apps.ai_chat.providers.factory import ProviderFactory
from apps.ai_chat.providers.mock_provider import MockAIProvider
from apps.ai_chat.providers.openai_compatible import OpenAICompatibleProvider
from apps.ai_chat.prompts import DISCLAIMER
from apps.pets.models import Pet
from apps.users.models import User


class BrokenProvider:
    provider_name = "broken"
    model = "broken-model"

    def chat(self, *args, **kwargs):
        raise AIProviderError("upstream exploded with sensitive details")


class TextProvider:
    provider_name = "text"
    model = "text-model"

    def chat(self, *args, **kwargs):
        return "这是一段无法解析为 JSON 的模型文本回复。"


class AIChatApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="ai-owner@example.com",
            password="StrongPass123",
            nickname="豆豆家长",
        )
        self.other_user = User.objects.create_user(
            email="other-ai-owner@example.com",
            password="StrongPass123",
            nickname="别的家长",
        )
        self.pet = Pet.objects.create(
            owner=self.user,
            name="豆豆",
            species=Pet.Species.CAT,
            breed="英短",
            gender=Pet.Gender.MALE,
            birthday=date(2024, 1, 1),
            weight="4.60",
            neutered=True,
        )
        self.other_pet = Pet.objects.create(
            owner=self.other_user,
            name="花花",
            species=Pet.Species.DOG,
            weight="8.10",
        )

    def authenticate(self, user=None):
        token = RefreshToken.for_user(user or self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_anonymous_cannot_access_ai_conversations(self):
        response = self.client.get(reverse("ai-conversation-list"))

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_create_ai_conversation(self):
        self.authenticate()
        response = self.client.post(
            reverse("ai-conversation-list"),
            {"pet_id": self.pet.id, "title": "猫咪呕吐咨询"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["code"], 0)
        self.assertEqual(AIConversation.objects.count(), 1)

    def test_user_cannot_access_other_users_ai_conversation(self):
        conversation = AIConversation.objects.create(
            user=self.other_user,
            pet=self.other_pet,
            title="别人的会话",
        )
        self.authenticate()

        response = self.client.get(reverse("ai-conversation-detail", args=[conversation.id]))

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_consult_with_other_users_pet(self):
        self.authenticate()
        response = self.client.post(
            reverse("ai-consult"),
            {
                "pet_id": self.other_pet.id,
                "message": "它今天拉稀了",
                "image_urls": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    @override_settings(AI_PROVIDER="mock", AI_API_KEY="")
    def test_user_can_consult_with_own_pet(self):
        self.authenticate()
        response = self.client.post(
            reverse("ai-consult"),
            {
                "pet_id": self.pet.id,
                "message": "猫咪今天吐了两次，精神一般",
                "image_urls": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn(data["result"]["risk_level"], {"low", "medium", "high", "unknown"})
        self.assertEqual(data["result"]["disclaimer"], DISCLAIMER)

    def test_openai_provider_missing_config_has_friendly_error(self):
        with self.assertRaises(AIConfigurationError):
            OpenAICompatibleProvider(
                api_base="https://example.com/v1",
                api_key="",
                model="example-model",
            )

    @override_settings(DEBUG=True, AI_PROVIDER="ark_openai_compatible", AI_API_KEY="")
    def test_debug_empty_api_key_falls_back_to_mock_provider(self):
        provider = ProviderFactory.create()

        self.assertIsInstance(provider, MockAIProvider)

    @override_settings(AI_PROVIDER="mock", AI_API_KEY="")
    def test_consult_saves_messages_and_result(self):
        self.authenticate()
        response = self.client.post(
            reverse("ai-consult"),
            {"pet_id": self.pet.id, "message": "狗狗拉稀一天了", "image_urls": []},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        conversation_id = response.json()["data"]["conversation_id"]
        self.assertTrue(
            AIMessage.objects.filter(
                conversation_id=conversation_id,
                role=AIMessage.Role.USER,
            ).exists()
        )
        self.assertTrue(
            AIMessage.objects.filter(
                conversation_id=conversation_id,
                role=AIMessage.Role.ASSISTANT,
            ).exists()
        )
        self.assertTrue(AIConsultationResult.objects.filter(conversation_id=conversation_id).exists())

    def test_model_failure_returns_friendly_error(self):
        self.authenticate()
        with patch("apps.ai_chat.services.ProviderFactory.create", return_value=BrokenProvider()):
            response = self.client.post(
                reverse("ai-consult"),
                {"pet_id": self.pet.id, "message": "猫咪精神不好", "image_urls": []},
                format="json",
            )

        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body["code"], 60001)
        self.assertNotIn("sensitive", body["message"])

    def test_invalid_json_reply_falls_back_without_crashing(self):
        self.authenticate()
        with patch("apps.ai_chat.services.ProviderFactory.create", return_value=TextProvider()):
            response = self.client.post(
                reverse("ai-consult"),
                {"pet_id": self.pet.id, "message": "猫咪不吃饭", "image_urls": []},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        result = response.json()["data"]["result"]
        self.assertEqual(result["risk_level"], "unknown")
        self.assertEqual(result["disclaimer"], DISCLAIMER)

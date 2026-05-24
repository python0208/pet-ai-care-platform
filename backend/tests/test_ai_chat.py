from datetime import date
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.ai_chat.models import (
    AIActionDraft,
    AIConsultationResult,
    AIConversation,
    AIMessage,
)
from apps.ai_chat.providers.base import AIConfigurationError, AIProviderError
from apps.ai_chat.providers.factory import ProviderFactory
from apps.ai_chat.providers.mock_provider import MockAIProvider
from apps.ai_chat.providers.openai_compatible import OpenAICompatibleProvider
from apps.ai_chat.prompts import DISCLAIMER
from apps.pets.models import HealthRecord, Pet, WeightRecord
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


class JsonProvider:
    provider_name = "json"
    model = "json-model"

    def __init__(self, payload):
        self.payload = payload

    def chat(self, *args, **kwargs):
        import json

        return json.dumps(self.payload, ensure_ascii=False)


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

    def test_conversation_list_includes_pending_action_count(self):
        conversation = AIConversation.objects.create(user=self.user, pet=self.pet, title="记录疫苗")
        AIActionDraft.objects.create(
            user=self.user,
            pet=self.pet,
            conversation=conversation,
            action_type=AIActionDraft.ActionType.CREATE_HEALTH_RECORD,
            display_title="建议添加疫苗记录",
            confirm_text="确认保存疫苗记录？",
            payload={
                "pet_id": self.pet.id,
                "record_type": "vaccine",
                "title": "疫苗记录",
                "record_date": "2026-05-24",
            },
        )
        AIActionDraft.objects.create(
            user=self.user,
            pet=self.pet,
            conversation=conversation,
            action_type=AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
            display_title="已保存体重记录",
            confirm_text="确认？",
            status=AIActionDraft.Status.EXECUTED,
            payload={"pet_id": self.pet.id, "weight": "4.80", "record_date": "2026-05-24"},
        )
        self.authenticate()

        response = self.client.get(reverse("ai-conversation-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"][0]["pending_action_count"], 1)

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
        self.assertEqual(data["mode"], "health_consultation")

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

    def test_daily_care_response_has_no_health_result(self):
        self.authenticate()
        payload = {
            "mode": "daily_care",
            "reply": "可以逐步换粮，先少量混入新粮，观察排便和食欲。",
            "health_result": None,
            "action_drafts": [],
            "questions_to_ask": [],
            "disclaimer": "如涉及健康问题，本结果仅供养宠护理参考，不能替代专业兽医诊断。",
        }
        with patch("apps.ai_chat.services.ProviderFactory.create", return_value=JsonProvider(payload)):
            response = self.client.post(
                reverse("ai-consult"),
                {"pet_id": self.pet.id, "message": "怎么给猫换粮", "image_urls": []},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["mode"], "daily_care")
        self.assertIsNone(data["health_result"])
        self.assertEqual(data["action_drafts"], [])

    def test_health_consultation_contains_disclaimer(self):
        self.authenticate()
        payload = {
            "mode": "health_consultation",
            "reply": "需要先观察精神和食欲。",
            "health_result": {
                "risk_level": "medium",
                "summary": "宠物出现呕吐，需要结合持续时间判断风险。",
                "possible_causes": ["饮食变化"],
                "home_care": ["观察精神", "保证饮水"],
                "need_vet": True,
                "warning_signs": ["持续呕吐"],
                "questions_to_ask": ["吐了几次？"],
                "disclaimer": DISCLAIMER,
            },
            "action_drafts": [],
            "questions_to_ask": [],
            "disclaimer": "如涉及健康问题，本结果仅供养宠护理参考，不能替代专业兽医诊断。",
        }
        with patch("apps.ai_chat.services.ProviderFactory.create", return_value=JsonProvider(payload)):
            response = self.client.post(
                reverse("ai-consult"),
                {"pet_id": self.pet.id, "message": "猫咪吐了", "image_urls": []},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["health_result"]["disclaimer"], DISCLAIMER)

    def test_record_intent_creates_action_draft(self):
        self.authenticate()
        payload = {
            "mode": "record_intent",
            "reply": "我可以帮你整理成体重记录草稿，确认后再保存。",
            "health_result": None,
            "action_drafts": [
                {
                    "action_type": "create_weight_record",
                    "display_title": "建议添加体重记录",
                    "confirm_text": "是否将豆豆今天体重 4.8kg 添加到体重记录？",
                    "payload": {
                        "pet_id": self.pet.id,
                        "record_type": "weight",
                        "weight": "4.80",
                        "record_date": "2026-05-24",
                        "remark": "用户通过 AI 对话记录",
                    },
                    "need_confirm": True,
                }
            ],
            "questions_to_ask": [],
            "disclaimer": "如涉及健康问题，本结果仅供养宠护理参考，不能替代专业兽医诊断。",
        }
        with patch("apps.ai_chat.services.ProviderFactory.create", return_value=JsonProvider(payload)):
            response = self.client.post(
                reverse("ai-consult"),
                {"pet_id": self.pet.id, "message": "记录豆豆今天体重 4.8kg", "image_urls": []},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        drafts = response.json()["data"]["action_drafts"]
        self.assertEqual(len(drafts), 1)
        self.assertEqual(AIActionDraft.objects.count(), 1)

    def test_chinese_health_record_payload_creates_action_draft(self):
        self.authenticate()
        payload = {
            "mode": "record_intent",
            "reply": "我可以帮你整理成驱虫记录草稿，确认后再保存。",
            "health_result": None,
            "action_drafts": [
                {
                    "action_type": "create_health_record",
                    "display_title": "建议添加驱虫记录",
                    "confirm_text": "",
                    "payload": {
                        "pet_id": self.pet.id,
                        "record_type": "驱虫",
                        "description": "今天做了体外驱虫",
                    },
                    "need_confirm": True,
                }
            ],
            "questions_to_ask": [],
            "disclaimer": "如涉及健康问题，本结果仅供养宠护理参考，不能替代专业兽医诊断。",
        }
        with patch("apps.ai_chat.services.ProviderFactory.create", return_value=JsonProvider(payload)):
            response = self.client.post(
                reverse("ai-consult"),
                {"pet_id": self.pet.id, "message": "记录今天做了体外驱虫", "image_urls": []},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        drafts = response.json()["data"]["action_drafts"]
        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0]["payload"]["record_type"], HealthRecord.RecordType.DEWORM)
        self.assertTrue(drafts[0]["payload"]["title"])
        self.assertTrue(drafts[0]["confirm_text"])

    def test_record_intent_without_model_draft_infers_vaccine_draft(self):
        self.authenticate()
        payload = {
            "mode": "record_intent",
            "reply": "我可以帮你整理成疫苗记录草稿，确认后再保存。",
            "health_result": None,
            "action_drafts": [],
            "questions_to_ask": [],
            "disclaimer": "如涉及健康问题，本结果仅供养宠护理参考，不能替代专业兽医诊断。",
        }
        with patch("apps.ai_chat.services.ProviderFactory.create", return_value=JsonProvider(payload)):
            response = self.client.post(
                reverse("ai-consult"),
                {"pet_id": self.pet.id, "message": "记录今天接种了疫苗", "image_urls": []},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        drafts = response.json()["data"]["action_drafts"]
        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0]["action_type"], AIActionDraft.ActionType.CREATE_HEALTH_RECORD)
        self.assertEqual(drafts[0]["payload"]["record_type"], HealthRecord.RecordType.VACCINE)

    def test_record_intent_without_model_draft_infers_allergy_draft(self):
        self.authenticate()
        payload = {
            "mode": "record_intent",
            "reply": "我可以帮你整理成过敏记录草稿，确认后再保存。",
            "health_result": None,
            "action_drafts": [],
            "questions_to_ask": [],
            "disclaimer": "如涉及健康问题，本结果仅供养宠护理参考，不能替代专业兽医诊断。",
        }
        with patch("apps.ai_chat.services.ProviderFactory.create", return_value=JsonProvider(payload)):
            response = self.client.post(
                reverse("ai-consult"),
                {"pet_id": self.pet.id, "message": "记录豆豆对鸡肉过敏", "image_urls": []},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        drafts = response.json()["data"]["action_drafts"]
        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0]["payload"]["record_type"], HealthRecord.RecordType.ALLERGY)
        self.assertIn("鸡肉", drafts[0]["payload"]["title"])

    def test_confirm_weight_record_action_draft_creates_weight_record(self):
        self.authenticate()
        conversation = AIConversation.objects.create(user=self.user, pet=self.pet, title="记录体重")
        draft = AIActionDraft.objects.create(
            user=self.user,
            pet=self.pet,
            conversation=conversation,
            action_type=AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
            display_title="建议添加体重记录",
            confirm_text="确认保存体重记录？",
            payload={
                "pet_id": self.pet.id,
                "record_type": "weight",
                "weight": "4.80",
                "record_date": "2026-05-24",
                "remark": "AI 记录",
            },
        )

        response = self.client.post(reverse("ai-action-draft-confirm", args=[draft.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(WeightRecord.objects.filter(pet=self.pet).count(), 1)
        draft.refresh_from_db()
        self.assertEqual(draft.status, AIActionDraft.Status.EXECUTED)
        self.assertEqual(draft.result_ref_type, "weight_record")

    def test_confirm_health_record_action_draft_creates_health_record(self):
        self.authenticate()
        conversation = AIConversation.objects.create(user=self.user, pet=self.pet, title="记录健康")
        draft = AIActionDraft.objects.create(
            user=self.user,
            pet=self.pet,
            conversation=conversation,
            action_type=AIActionDraft.ActionType.CREATE_HEALTH_RECORD,
            display_title="建议添加健康记录",
            confirm_text="确认保存健康记录？",
            payload={
                "pet_id": self.pet.id,
                "record_type": "medical",
                "title": "夜间异常活跃",
                "record_date": "2026-05-24",
                "description": "今天不睡觉，夜间异常活跃。",
                "attachments": [],
            },
        )

        response = self.client.post(reverse("ai-action-draft-confirm", args=[draft.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(HealthRecord.objects.filter(pet=self.pet).count(), 1)
        draft.refresh_from_db()
        self.assertEqual(draft.status, AIActionDraft.Status.EXECUTED)
        self.assertEqual(draft.result_ref_type, "health_record")

    def test_user_cannot_confirm_other_users_action_draft(self):
        conversation = AIConversation.objects.create(user=self.other_user, pet=self.other_pet, title="别人的草稿")
        draft = AIActionDraft.objects.create(
            user=self.other_user,
            pet=self.other_pet,
            conversation=conversation,
            action_type=AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
            display_title="建议添加体重记录",
            confirm_text="确认？",
            payload={"pet_id": self.other_pet.id, "weight": "8.30", "record_date": "2026-05-24"},
        )
        self.authenticate()

        response = self.client.post(reverse("ai-action-draft-confirm", args=[draft.id]))

        self.assertEqual(response.status_code, 404)

    def test_action_draft_cannot_write_to_other_users_pet(self):
        self.authenticate()
        conversation = AIConversation.objects.create(user=self.user, pet=self.pet, title="恶意草稿")
        draft = AIActionDraft.objects.create(
            user=self.user,
            pet=self.pet,
            conversation=conversation,
            action_type=AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
            display_title="建议添加体重记录",
            confirm_text="确认？",
            payload={"pet_id": self.other_pet.id, "weight": "8.30", "record_date": "2026-05-24"},
        )

        response = self.client.post(reverse("ai-action-draft-confirm", args=[draft.id]))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(WeightRecord.objects.count(), 0)

    def test_executed_action_draft_cannot_run_twice(self):
        self.authenticate()
        conversation = AIConversation.objects.create(user=self.user, pet=self.pet, title="记录体重")
        draft = AIActionDraft.objects.create(
            user=self.user,
            pet=self.pet,
            conversation=conversation,
            action_type=AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
            display_title="建议添加体重记录",
            confirm_text="确认？",
            payload={"pet_id": self.pet.id, "weight": "4.80", "record_date": "2026-05-24"},
        )
        self.client.post(reverse("ai-action-draft-confirm", args=[draft.id]))
        response = self.client.post(reverse("ai-action-draft-confirm", args=[draft.id]))

        self.assertEqual(response.status_code, 409)
        self.assertEqual(WeightRecord.objects.count(), 1)

    def test_cancelled_action_draft_cannot_execute(self):
        self.authenticate()
        conversation = AIConversation.objects.create(user=self.user, pet=self.pet, title="记录体重")
        draft = AIActionDraft.objects.create(
            user=self.user,
            pet=self.pet,
            conversation=conversation,
            action_type=AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
            display_title="建议添加体重记录",
            confirm_text="确认？",
            payload={"pet_id": self.pet.id, "weight": "4.80", "record_date": "2026-05-24"},
        )
        cancel_response = self.client.post(reverse("ai-action-draft-cancel", args=[draft.id]))
        confirm_response = self.client.post(reverse("ai-action-draft-confirm", args=[draft.id]))

        self.assertEqual(cancel_response.status_code, 200)
        self.assertEqual(confirm_response.status_code, 409)
        self.assertEqual(WeightRecord.objects.count(), 0)

    def test_invalid_payload_does_not_create_record(self):
        self.authenticate()
        conversation = AIConversation.objects.create(user=self.user, pet=self.pet, title="坏草稿")
        draft = AIActionDraft.objects.create(
            user=self.user,
            pet=self.pet,
            conversation=conversation,
            action_type=AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
            display_title="建议添加体重记录",
            confirm_text="确认？",
            payload={"pet_id": self.pet.id, "weight": "-1", "record_date": "2026-05-24"},
        )

        response = self.client.post(reverse("ai-action-draft-confirm", args=[draft.id]))

        self.assertEqual(response.status_code, 409)
        self.assertEqual(WeightRecord.objects.count(), 0)

    @override_settings(AI_PROVIDER="mock", AI_API_KEY="")
    def test_image_urls_are_saved_to_user_message(self):
        self.authenticate()
        response = self.client.post(
            reverse("ai-consult"),
            {
                "pet_id": self.pet.id,
                "message": "看看这张图片",
                "image_urls": ["/media/uploads/ai/test.png"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        user_message = AIMessage.objects.filter(role=AIMessage.Role.USER).latest("id")
        self.assertEqual(user_message.image_urls, ["/media/uploads/ai/test.png"])

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

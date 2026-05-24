from rest_framework import serializers

from apps.ai_chat.models import (
    AIActionDraft,
    AIConsultationResult,
    AIConversation,
    AIMessage,
)
from apps.pets.models import Pet


class AIConversationSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source="pet.name", read_only=True)
    pending_action_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = AIConversation
        fields = (
            "id",
            "pet",
            "pet_name",
            "title",
            "model_provider",
            "model_name",
            "status",
            "pending_action_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "pet_name",
            "model_provider",
            "model_name",
            "status",
            "pending_action_count",
            "created_at",
            "updated_at",
        )


class AIConversationCreateSerializer(serializers.Serializer):
    pet_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(max_length=128, required=False, allow_blank=True)

    def validate_pet_id(self, value):
        if value is None:
            return value
        user = self.context["request"].user
        if not Pet.objects.filter(id=value, owner=user).exists():
            raise serializers.ValidationError("宠物不存在")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        pet_id = validated_data.get("pet_id")
        pet = Pet.objects.filter(id=pet_id, owner=user).first() if pet_id else None
        return AIConversation.objects.create(
            user=user,
            pet=pet,
            title=validated_data.get("title") or "AI 健康咨询",
        )


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = (
            "id",
            "conversation",
            "role",
            "content",
            "image_urls",
            "raw_response",
            "created_at",
        )
        read_only_fields = ("id", "conversation", "role", "raw_response", "created_at")


class AIActionDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIActionDraft
        fields = (
            "id",
            "conversation",
            "pet",
            "source_message",
            "action_type",
            "display_title",
            "confirm_text",
            "payload",
            "status",
            "result_ref_type",
            "result_ref_id",
            "error_message",
            "created_at",
            "updated_at",
            "executed_at",
        )
        read_only_fields = fields


class ConsultationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConsultationResult
        fields = (
            "risk_level",
            "summary",
            "possible_causes",
            "home_care",
            "need_vet",
            "warning_signs",
            "questions_to_ask",
            "disclaimer",
        )


class ConsultSerializer(serializers.Serializer):
    pet_id = serializers.IntegerField()
    conversation_id = serializers.IntegerField(required=False, allow_null=True)
    message = serializers.CharField(max_length=4000, allow_blank=True, required=False)
    image_urls = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
    )

    def validate_pet_id(self, value):
        user = self.context["request"].user
        if not Pet.objects.filter(id=value, owner=user).exists():
            raise serializers.ValidationError("宠物不存在")
        return value

    def validate_image_urls(self, value):
        return value or []

    def validate(self, attrs):
        message = (attrs.get("message") or "").strip()
        image_urls = attrs.get("image_urls") or []
        if not message and not image_urls:
            raise serializers.ValidationError("请描述问题或上传图片")
        attrs["message"] = message
        attrs["image_urls"] = image_urls
        return attrs


class ConversationMessageCreateSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=4000, allow_blank=True, required=False)
    image_urls = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        allow_empty=True,
    )

    def validate_image_urls(self, value):
        return value or []

    def validate(self, attrs):
        message = (attrs.get("message") or "").strip()
        image_urls = attrs.get("image_urls") or []
        if not message and not image_urls:
            raise serializers.ValidationError("请描述问题或上传图片")
        attrs["message"] = message
        attrs["image_urls"] = image_urls
        return attrs

from rest_framework import permissions, status
from rest_framework.views import APIView

from apps.ai_chat.models import AIConversation
from apps.ai_chat.providers.base import AIProviderError
from apps.ai_chat.serializers import (
    AIConversationCreateSerializer,
    AIConversationSerializer,
    AIMessageSerializer,
    ConsultationResultSerializer,
    ConsultSerializer,
    ConversationMessageCreateSerializer,
)
from apps.ai_chat.services import consult_pet_health, get_owned_conversation
from apps.common.responses import error_response, success_response


class AIConversationListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        conversations = AIConversation.objects.filter(
            user=request.user,
            status__in=[AIConversation.Status.ACTIVE, AIConversation.Status.ARCHIVED],
        ).select_related("pet")
        return success_response(AIConversationSerializer(conversations, many=True).data)

    def post(self, request):
        serializer = AIConversationCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        return success_response(
            AIConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED,
        )


class AIConversationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        conversation = get_owned_conversation(request.user, pk)
        return success_response(AIConversationSerializer(conversation).data)

    def delete(self, request, pk):
        conversation = get_owned_conversation(request.user, pk)
        conversation.status = AIConversation.Status.DELETED
        conversation.save(update_fields=["status", "updated_at"])
        return success_response({})


class AIConversationMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        conversation = get_owned_conversation(request.user, pk)
        messages = conversation.messages.all()
        return success_response(AIMessageSerializer(messages, many=True).data)

    def post(self, request, pk):
        conversation = get_owned_conversation(request.user, pk)
        if not conversation.pet_id:
            return error_response(
                code=40001,
                message="请先选择宠物后再咨询",
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ConversationMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return run_consult(
            request=request,
            pet_id=conversation.pet_id,
            message=serializer.validated_data["message"],
            image_urls=serializer.validated_data.get("image_urls") or [],
            conversation_id=conversation.id,
        )


class AIConsultView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ConsultSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return run_consult(
            request=request,
            pet_id=serializer.validated_data["pet_id"],
            message=serializer.validated_data["message"],
            image_urls=serializer.validated_data.get("image_urls") or [],
            conversation_id=serializer.validated_data.get("conversation_id"),
        )


def run_consult(request, pet_id, message, image_urls, conversation_id=None):
    try:
        payload = consult_pet_health(
            user=request.user,
            pet_id=pet_id,
            message=message,
            image_urls=image_urls,
            conversation_id=conversation_id,
        )
    except AIProviderError:
        return error_response(
            code=60001,
            message="AI 服务暂时不可用，请稍后重试",
            errors={},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return success_response(
        {
            "conversation_id": payload.conversation.id,
            "message_id": payload.assistant_message.id,
            "reply": payload.reply,
            "result": ConsultationResultSerializer(payload.result).data,
        }
    )

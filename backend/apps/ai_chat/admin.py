from django.contrib import admin

from apps.ai_chat.models import (
    AIActionDraft,
    AIConsultationResult,
    AIConversation,
    AIMessage,
    PromptTemplate,
)


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "pet", "title", "model_provider", "model_name", "status", "created_at")
    list_filter = ("status", "model_provider", "model_name")
    search_fields = ("title", "user__email", "pet__name")


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("content",)


@admin.register(AIConsultationResult)
class AIConsultationResultAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "risk_level", "need_vet", "created_at")
    list_filter = ("risk_level", "need_vet")
    search_fields = ("summary",)


@admin.register(AIActionDraft)
class AIActionDraftAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "pet", "action_type", "status", "result_ref_type", "result_ref_id", "created_at")
    list_filter = ("action_type", "status")
    search_fields = ("display_title", "confirm_text", "user__email", "pet__name")


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "scene", "version", "is_active", "updated_at")
    list_filter = ("scene", "is_active")
    search_fields = ("name", "content")

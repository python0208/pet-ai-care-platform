from django.contrib import admin

from apps.ai_chat.models import (
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


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "scene", "version", "is_active", "updated_at")
    list_filter = ("scene", "is_active")
    search_fields = ("name", "content")

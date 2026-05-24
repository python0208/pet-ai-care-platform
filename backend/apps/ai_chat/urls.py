from django.urls import path

from apps.ai_chat.views import (
    AIActionDraftCancelView,
    AIActionDraftConfirmView,
    AIConsultView,
    AIConversationActionDraftsView,
    AIConversationDetailView,
    AIConversationListCreateView,
    AIConversationMessagesView,
)

urlpatterns = [
    path("ai/conversations/", AIConversationListCreateView.as_view(), name="ai-conversation-list"),
    path("ai/conversations/<int:pk>/", AIConversationDetailView.as_view(), name="ai-conversation-detail"),
    path(
        "ai/conversations/<int:pk>/messages/",
        AIConversationMessagesView.as_view(),
        name="ai-conversation-messages",
    ),
    path(
        "ai/conversations/<int:pk>/action-drafts/",
        AIConversationActionDraftsView.as_view(),
        name="ai-conversation-action-drafts",
    ),
    path(
        "ai/action-drafts/<int:pk>/confirm/",
        AIActionDraftConfirmView.as_view(),
        name="ai-action-draft-confirm",
    ),
    path(
        "ai/action-drafts/<int:pk>/cancel/",
        AIActionDraftCancelView.as_view(),
        name="ai-action-draft-cancel",
    ),
    path("ai/consult/", AIConsultView.as_view(), name="ai-consult"),
]

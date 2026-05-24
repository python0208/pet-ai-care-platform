from django.urls import path

from apps.ai_chat.views import (
    AIConsultView,
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
    path("ai/consult/", AIConsultView.as_view(), name="ai-consult"),
]

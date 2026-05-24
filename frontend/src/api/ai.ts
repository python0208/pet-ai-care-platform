import { request } from "@/api/request";
import type {
  AIConsultPayload,
  AIConsultResponse,
  AIConversation,
  AIMessage,
} from "@/types/ai";

export function getConversations() {
  return request<AIConversation[]>("/ai/conversations/");
}

export function createConversation(data: { pet_id?: number | null; title?: string }) {
  return request<AIConversation>("/ai/conversations/", {
    method: "POST",
    data,
    loading: true,
  });
}

export function getConversation(id: number | string) {
  return request<AIConversation>(`/ai/conversations/${id}/`);
}

export function getConversationMessages(id: number | string) {
  return request<AIMessage[]>(`/ai/conversations/${id}/messages/`);
}

export function sendConversationMessage(
  id: number | string,
  data: { message: string; image_urls?: string[] },
) {
  return request<AIConsultResponse>(`/ai/conversations/${id}/messages/`, {
    method: "POST",
    data,
    loading: true,
  });
}

export function consultAI(data: AIConsultPayload) {
  return request<AIConsultResponse>("/ai/consult/", {
    method: "POST",
    data,
    loading: true,
  });
}

export function deleteConversation(id: number | string) {
  return request<Record<string, never>>(`/ai/conversations/${id}/`, {
    method: "DELETE",
    loading: true,
  });
}

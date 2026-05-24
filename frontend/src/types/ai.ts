export type AIRiskLevel = "low" | "medium" | "high" | "unknown";

export interface AIConversation {
  id: number;
  pet: number | null;
  pet_name: string;
  title: string;
  model_provider: string;
  model_name: string;
  status: "active" | "archived" | "deleted";
  created_at: string;
  updated_at: string;
}

export interface AIMessage {
  id: number;
  conversation: number;
  role: "system" | "user" | "assistant";
  content: string;
  image_urls: string[];
  created_at: string;
}

export interface AIConsultationResult {
  risk_level: AIRiskLevel;
  summary: string;
  possible_causes: string[];
  home_care: string[];
  need_vet: boolean;
  warning_signs: string[];
  questions_to_ask: string[];
  disclaimer: string;
}

export interface AIConsultResponse {
  conversation_id: number;
  message_id: number;
  reply: string;
  result: AIConsultationResult;
}

export interface AIConsultPayload {
  pet_id: number;
  conversation_id?: number | null;
  message: string;
  image_urls?: string[];
}

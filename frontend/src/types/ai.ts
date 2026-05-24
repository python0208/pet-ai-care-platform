export type AIRiskLevel = "low" | "medium" | "high" | "unknown";

export interface AIConversation {
  id: number;
  pet: number | null;
  pet_name: string;
  title: string;
  model_provider: string;
  model_name: string;
  status: "active" | "archived" | "deleted";
  pending_action_count?: number;
  created_at: string;
  updated_at: string;
}

export interface AIMessage {
  id: number;
  conversation: number;
  role: "system" | "user" | "assistant";
  content: string;
  image_urls: string[];
  raw_response?: {
    parsed_result?: AIParsedResponse;
    raw_text?: string;
  } | null;
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

export type AIMode = "daily_care" | "health_consultation" | "record_intent" | "mixed" | "unknown";
export type AIActionType = "create_weight_record" | "create_health_record";
export type AIActionDraftStatus = "pending" | "confirmed" | "cancelled" | "executed" | "failed";

export interface AIActionDraft {
  id: number;
  conversation: number;
  pet: number;
  source_message: number | null;
  action_type: AIActionType;
  display_title: string;
  confirm_text: string;
  payload: Record<string, any>;
  status: AIActionDraftStatus;
  result_ref_type: string;
  result_ref_id: number | null;
  error_message: string;
  created_at: string;
  updated_at: string;
  executed_at: string | null;
}

export interface AIParsedResponse {
  mode: AIMode;
  reply: string;
  health_result: AIConsultationResult | null;
  action_drafts: Array<Omit<AIActionDraft, "id" | "conversation" | "pet" | "status" | "result_ref_type" | "result_ref_id" | "error_message" | "created_at" | "updated_at" | "executed_at">>;
  questions_to_ask: string[];
  disclaimer: string;
}

export interface AIConsultResponse {
  conversation_id: number;
  message_id: number;
  reply: string;
  mode: AIMode;
  health_result: AIConsultationResult | null;
  action_drafts: AIActionDraft[];
  questions_to_ask: string[];
  disclaimer: string;
  result: AIConsultationResult;
}

export interface AIConsultPayload {
  pet_id: number;
  conversation_id?: number | null;
  message: string;
  image_urls?: string[];
}

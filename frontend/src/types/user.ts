export interface UserProfile {
  id: number;
  email: string;
  nickname: string;
  avatar: string;
  gender: "unknown" | "male" | "female";
  is_email_verified: boolean;
  has_wechat_bound: boolean;
  auth_providers: string[];
}

export interface AuthPayload {
  access_token: string;
  refresh_token: string;
  user: UserProfile;
  is_new_user?: boolean;
}

export interface WechatLoginPayload {
  code: string;
  platform: "miniapp" | "app";
  nickname?: string;
  avatar?: string;
}

export interface UserSummary {
  pet_count: number;
  ai_conversation_count: number;
  pending_action_count: number;
  has_wechat_bound: boolean;
}

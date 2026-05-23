export interface UserProfile {
  id: number;
  email: string;
  nickname: string;
  avatar: string;
  gender: "unknown" | "male" | "female";
  is_email_verified: boolean;
}

export interface AuthPayload {
  access_token: string;
  refresh_token: string;
  user: UserProfile;
}

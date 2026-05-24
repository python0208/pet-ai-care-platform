import { request } from "@/api/request";
import type { AuthPayload, UserProfile, UserSummary, WechatLoginPayload } from "@/types/user";

export interface RegisterPayload {
  email: string;
  password: string;
  confirm_password: string;
  nickname?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface ProfileUpdatePayload {
  nickname?: string;
  avatar?: string;
  gender?: "unknown" | "male" | "female";
}

export function register(payload: RegisterPayload) {
  return request<AuthPayload>("/auth/register/", {
    method: "POST",
    data: payload,
    loading: true,
  });
}

export function login(payload: LoginPayload) {
  return request<AuthPayload>("/auth/login/", {
    method: "POST",
    data: payload,
    loading: true,
  });
}

export function wechatLogin(payload: WechatLoginPayload) {
  return request<AuthPayload>("/auth/wx-login/", {
    method: "POST",
    data: payload,
    loading: true,
  });
}

export function getMe() {
  return request<UserProfile>("/users/me/");
}

export function getUserSummary() {
  return request<UserSummary>("/users/me/summary/");
}

export function updateMe(payload: ProfileUpdatePayload) {
  return request<UserProfile>("/users/me/", {
    method: "PUT",
    data: payload,
    loading: true,
  });
}

export function logout() {
  return request<Record<string, never>>("/auth/logout/", {
    method: "POST",
  });
}

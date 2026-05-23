import { defineStore } from "pinia";

import { getMe } from "@/api/auth";
import type { AuthPayload, UserProfile } from "@/types/user";

interface AuthState {
  user: UserProfile | null;
  accessToken: string;
  refreshToken: string;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user: null,
    accessToken: uni.getStorageSync("access_token") || "",
    refreshToken: uni.getStorageSync("refresh_token") || "",
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.accessToken),
  },
  actions: {
    setAuth(payload: AuthPayload) {
      this.accessToken = payload.access_token;
      this.refreshToken = payload.refresh_token;
      this.user = payload.user;
      uni.setStorageSync("access_token", payload.access_token);
      uni.setStorageSync("refresh_token", payload.refresh_token);
    },
    clearAuth() {
      this.user = null;
      this.accessToken = "";
      this.refreshToken = "";
      uni.removeStorageSync("access_token");
      uni.removeStorageSync("refresh_token");
    },
    async fetchMe() {
      const response = await getMe();
      this.user = response.data;
      return response.data;
    },
  },
});

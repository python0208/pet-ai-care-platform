import { defineStore } from "pinia";

export const useAppStore = defineStore("app", {
  state: () => ({
    backendStatus: "checking" as "checking" | "ok" | "error",
  }),
  actions: {
    setBackendStatus(status: "checking" | "ok" | "error") {
      this.backendStatus = status;
    },
  },
});

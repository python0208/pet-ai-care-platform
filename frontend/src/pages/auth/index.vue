<template>
  <view class="auth-page">
    <view class="auth-shell">
      <view class="brand-block">
        <image class="planet" src="/static/icons/png/logo_star_planet.png" mode="aspectFit" />
        <text class="brand-title">宠护星球</text>
        <text class="brand-subtitle">用邮箱开启你的养宠小宇宙</text>
      </view>

      <view class="auth-card">
        <view class="tabs">
          <button
            class="tab-button"
            :class="{ active: mode === 'login' }"
            hover-class="button-tap"
            @tap="mode = 'login'"
          >
            登录
          </button>
          <button
            class="tab-button"
            :class="{ active: mode === 'register' }"
            hover-class="button-tap"
            @tap="mode = 'register'"
          >
            注册
          </button>
        </view>

        <view class="form-stack">
          <view class="field">
            <text class="field-label">邮箱</text>
            <input
              class="field-input"
              type="text"
              placeholder="name@example.com"
              :value="form.email"
              @input="onInput('email', $event)"
            />
          </view>

          <view v-if="mode === 'register'" class="field">
            <text class="field-label">昵称</text>
            <input
              class="field-input"
              type="text"
              placeholder="给自己起个养宠昵称"
              :value="form.nickname"
              @input="onInput('nickname', $event)"
            />
          </view>

          <view class="field">
            <text class="field-label">密码</text>
            <input
              class="field-input"
              type="safe-password"
              password
              placeholder="至少 8 位"
              :value="form.password"
              @input="onInput('password', $event)"
            />
          </view>

          <view v-if="mode === 'register'" class="field">
            <text class="field-label">确认密码</text>
            <input
              class="field-input"
              type="safe-password"
              password
              placeholder="再次输入密码"
              :value="form.confirmPassword"
              @input="onInput('confirmPassword', $event)"
            />
          </view>

          <view v-if="mode === 'register'" class="agreement" @tap="agreed = !agreed">
            <view class="checkbox" :class="{ checked: agreed }"></view>
            <text>我已阅读并同意用户协议和隐私政策</text>
          </view>

          <button class="primary-button" hover-class="button-tap" @tap="submit">
            {{ mode === "login" ? "登录" : "注册并进入" }}
          </button>

          <view v-if="showWechatArea" class="wechat-line">
            <view class="line"></view>
            <text>其他登录方式</text>
            <view class="line"></view>
          </view>

          <button
            v-if="isMiniApp"
            class="wechat-button"
            hover-class="button-tap"
            @tap="handleWechatLogin(false)"
          >
            微信一键登录
          </button>

          <button
            v-else-if="isDevMode"
            class="wechat-button mock"
            hover-class="button-tap"
            @tap="handleWechatLogin(true)"
          >
            开发模式微信登录
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";

import { login, register, wechatLogin } from "@/api/auth";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const mode = ref<"login" | "register">("login");
const agreed = ref(false);
const isMiniApp = ref(false);
const isDevMode = import.meta.env.DEV;
const showWechatArea = computed(() => isMiniApp.value || isDevMode);
const form = reactive({
  email: "",
  nickname: "",
  password: "",
  confirmPassword: "",
});

// #ifdef MP-WEIXIN
isMiniApp.value = true;
// #endif

type FormKey = keyof typeof form;
type InputEvent = Event & { detail?: { value?: string } };

function onInput(key: FormKey, event: Event) {
  form[key] = ((event as InputEvent).detail?.value || "") as never;
}

function showError(title: string) {
  uni.showToast({
    title,
    icon: "none",
  });
}

function validateBase() {
  if (!form.email.trim()) {
    showError("请填写邮箱");
    return false;
  }
  if (!form.password) {
    showError("请填写密码");
    return false;
  }
  if (form.password.length < 8) {
    showError("密码至少 8 位");
    return false;
  }
  return true;
}

async function submit() {
  if (!validateBase()) {
    return;
  }

  if (mode.value === "register") {
    if (form.password !== form.confirmPassword) {
      showError("两次密码不一致");
      return;
    }
    if (!agreed.value) {
      showError("请先同意用户协议");
      return;
    }
  }

  try {
    const response =
      mode.value === "login"
        ? await login({ email: form.email.trim(), password: form.password })
        : await register({
            email: form.email.trim(),
            nickname: form.nickname.trim(),
            password: form.password,
            confirm_password: form.confirmPassword,
          });
    authStore.setAuth(response.data);
    uni.switchTab({ url: "/pages/user/index" });
  } catch (error) {
    const message = (error as { message?: string })?.message || "操作失败，请稍后再试";
    showError(message);
  }
}

function getMiniappLoginCode() {
  return new Promise<string>((resolve, reject) => {
    uni.login({
      provider: "weixin",
      success: (result: any) => {
        if (result.code) {
          resolve(result.code);
          return;
        }
        reject(new Error("未获取到微信登录凭证"));
      },
      fail: reject,
    } as any);
  });
}

async function handleWechatLogin(useMock: boolean) {
  try {
    const code = useMock ? "mock-wx-code" : await getMiniappLoginCode();
    const response = await wechatLogin({
      code,
      platform: "miniapp",
      nickname: "微信用户",
      avatar: "",
    });
    authStore.setAuth(response.data);
    uni.showToast({ title: "登录成功", icon: "success" });
    uni.switchTab({ url: "/pages/user/index" });
  } catch (error) {
    const message = (error as { message?: string })?.message || "微信登录失败，请稍后再试";
    showError(message);
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 82% 12%, rgba(255, 213, 155, 0.34), transparent 190rpx),
    radial-gradient(circle at 10% 0%, rgba(174, 224, 255, 0.8), transparent 260rpx),
    linear-gradient(180deg, #eef8ff 0%, #fbfdff 100%);
}

.auth-shell {
  min-height: 100vh;
  padding: 84rpx 34rpx 48rpx;
}

.brand-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 42rpx;
}

.planet {
  width: 86rpx;
  height: 86rpx;
  margin-bottom: 14rpx;
}

.brand-title {
  color: #10172d;
  font-size: 48rpx;
  font-weight: 900;
}

.brand-subtitle {
  margin-top: 12rpx;
  color: #64748b;
  font-size: 26rpx;
}

.auth-card {
  padding: 28rpx;
  border-radius: 38rpx;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 24rpx 58rpx rgba(30, 119, 188, 0.13);
}

.tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14rpx;
  padding: 8rpx;
  border-radius: 999rpx;
  background: #edf6ff;
}

.tab-button {
  height: 72rpx;
  border-radius: 999rpx;
  color: #69778f;
  font-size: 28rpx;
  font-weight: 800;
}

.tab-button.active {
  background: #1f8cff;
  color: #fff;
  box-shadow: 0 10rpx 24rpx rgba(31, 140, 255, 0.24);
}

.form-stack {
  padding-top: 30rpx;
}

.field {
  margin-bottom: 22rpx;
}

.field-label {
  display: block;
  margin: 0 0 12rpx 8rpx;
  color: #25304a;
  font-size: 24rpx;
  font-weight: 800;
}

.field-input {
  height: 88rpx;
  padding: 0 28rpx;
  border: 1rpx solid #e4edf7;
  border-radius: 26rpx;
  background: #f8fbff;
  color: #111827;
  font-size: 28rpx;
}

.agreement {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin: 4rpx 0 26rpx;
  color: #6b768b;
  font-size: 23rpx;
}

.checkbox {
  width: 32rpx;
  height: 32rpx;
  border: 3rpx solid #b9c9dc;
  border-radius: 10rpx;
  background: #fff;
}

.checkbox.checked {
  border-color: #1f8cff;
  background: #1f8cff;
  box-shadow: inset 0 0 0 7rpx #fff;
}

.primary-button {
  height: 88rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1476ff, #1f8cff);
  color: #fff;
  font-size: 30rpx;
  font-weight: 900;
  box-shadow: 0 18rpx 30rpx rgba(31, 140, 255, 0.24);
}

.wechat-line {
  display: flex;
  align-items: center;
  gap: 18rpx;
  margin-top: 28rpx;
  color: #9aa7b8;
  font-size: 22rpx;
}

.wechat-button {
  height: 82rpx;
  margin-top: 22rpx;
  border: 1rpx solid #bfe8d4;
  border-radius: 999rpx;
  background: #f2fff8;
  color: #19a35b;
  font-size: 28rpx;
  font-weight: 850;
}

.wechat-button.mock {
  border-color: #cde7ff;
  background: #f3f9ff;
  color: #1f8cff;
}

.line {
  flex: 1;
  height: 1rpx;
  background: #e5eef8;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

<template>
  <view class="user-page">
    <view class="page-header">
      <text class="page-title">我的</text>
      <text class="page-subtitle">管理账号、宠物档案和咨询记录</text>
    </view>

    <view class="profile-card">
      <image class="avatar" :src="avatarUrl" mode="aspectFill" />
      <view class="profile-main">
        <text class="nickname">{{ profileTitle }}</text>
        <text class="profile-subtitle">{{ profileSubtitle }}</text>
        <view v-if="isLoggedIn" class="tag-row">
          <text v-for="tag in providerTags" :key="tag" class="provider-tag">{{ tag }}</text>
          <text class="wechat-status" :class="{ bound: user?.has_wechat_bound }">
            {{ user?.has_wechat_bound ? "已绑定微信" : "未绑定微信" }}
          </text>
        </view>
      </view>
      <button
        v-if="isLoggedIn"
        class="edit-button"
        hover-class="button-tap"
        @tap="showTodo('资料编辑')"
      >
        编辑
      </button>
    </view>

    <view v-if="!isLoggedIn" class="login-actions">
      <button class="primary-button" hover-class="button-tap" @tap="goAuth">
        邮箱登录 / 注册
      </button>
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

    <view v-if="isLoggedIn" class="stats-card">
      <view class="stat-item" hover-class="button-tap" @tap="goPets">
        <text class="stat-number">{{ summary.pet_count }}</text>
        <text class="stat-label">我的宠物</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item" hover-class="button-tap" @tap="goAi">
        <text class="stat-number">{{ summary.ai_conversation_count }}</text>
        <text class="stat-label">咨询记录</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item" hover-class="button-tap" @tap="goAi">
        <text class="stat-number accent">{{ summary.pending_action_count }}</text>
        <text class="stat-label">待确认记录</text>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">养宠管理</view>
      <view
        v-for="item in petMenus"
        :key="item.title"
        class="menu-row"
        hover-class="button-tap"
        @tap="item.action"
      >
        <view class="menu-icon" :class="item.color">{{ item.icon }}</view>
        <view class="menu-text">
          <text class="menu-title">{{ item.title }}</text>
          <text class="menu-desc">{{ item.desc }}</text>
        </view>
        <text class="chevron">›</text>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">服务与商城</view>
      <view
        v-for="item in serviceMenus"
        :key="item.title"
        class="menu-row"
        hover-class="button-tap"
        @tap="showTodo(item.title)"
      >
        <view class="menu-icon" :class="item.color">{{ item.icon }}</view>
        <view class="menu-text">
          <text class="menu-title">{{ item.title }}</text>
          <text class="menu-desc">{{ item.desc }}</text>
        </view>
        <text class="chevron">›</text>
      </view>
    </view>

    <view class="section-card">
      <view class="section-title">设置</view>
      <view
        v-for="item in settingMenus"
        :key="item.title"
        class="menu-row"
        hover-class="button-tap"
        @tap="item.action"
      >
        <view class="menu-icon" :class="item.color">{{ item.icon }}</view>
        <view class="menu-text">
          <text class="menu-title">{{ item.title }}</text>
          <text class="menu-desc">{{ item.desc }}</text>
        </view>
        <text class="chevron">›</text>
      </view>
    </view>

    <button
      v-if="isLoggedIn"
      class="logout-button"
      hover-class="button-tap"
      @tap="confirmLogout"
    >
      退出登录
    </button>
  </view>
</template>

<script setup lang="ts">
import { onShow } from "@dcloudio/uni-app";
import { computed, reactive, ref } from "vue";

import { getUserSummary, logout, wechatLogin } from "@/api/auth";
import { resolveMediaUrl } from "@/api/request";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const user = computed(() => authStore.user);
const isLoggedIn = computed(() => authStore.isLoggedIn);
const isMiniApp = ref(false);
const isDevMode = import.meta.env.DEV;
const summary = reactive({
  pet_count: 0,
  ai_conversation_count: 0,
  pending_action_count: 0,
  has_wechat_bound: false,
});

// #ifdef MP-WEIXIN
isMiniApp.value = true;
// #endif

const avatarUrl = computed(() => {
  const avatar = user.value?.avatar;
  return avatar ? resolveMediaUrl(avatar) : "/static/images/default-user-avatar.svg";
});

const profileTitle = computed(() => {
  if (!isLoggedIn.value) {
    return "欢迎来到宠护星球";
  }
  return user.value?.nickname || (user.value?.has_wechat_bound ? "微信用户" : "宠护用户");
});

const profileSubtitle = computed(() => {
  if (!isLoggedIn.value) {
    return "登录后同步宠物档案与健康记录";
  }
  return user.value?.email || "未绑定邮箱";
});

const providerTags = computed(() => {
  const providers = user.value?.auth_providers || [];
  const tags: string[] = [];
  if (providers.includes("email")) {
    tags.push("邮箱登录");
  }
  if (providers.includes("wechat")) {
    tags.push("微信登录");
  }
  return tags.length ? tags : ["账号登录"];
});

const petMenus = [
  { title: "我的宠物", desc: "查看和切换宠物档案", icon: "宠", color: "blue", action: goPets },
  { title: "健康记录", desc: "疫苗、驱虫、就诊和过敏", icon: "+", color: "green", action: goPets },
  { title: "体重曲线", desc: "查看体重变化趋势", icon: "重", color: "orange", action: goPets },
  { title: "AI咨询记录", desc: "回看养护和健康咨询", icon: "AI", color: "blue", action: goAi },
  { title: "待确认记录", desc: "确认 AI 整理的档案草稿", icon: "✓", color: "green", action: goAi },
];

const serviceMenus = [
  { title: "我的订单", desc: "商城订单后续开放", icon: "包", color: "gray" },
  { title: "服务预约", desc: "洗护、医院预约后续开放", icon: "约", color: "orange" },
  { title: "收货地址", desc: "商城配送地址后续开放", icon: "址", color: "blue" },
  { title: "优惠券", desc: "活动权益后续开放", icon: "券", color: "green" },
];

const settingMenus = [
  { title: "账号安全", desc: "邮箱和登录状态", icon: "锁", color: "blue", action: () => showTodo("账号安全") },
  { title: "微信绑定", desc: "绑定或查看微信登录状态", icon: "微", color: "green", action: handleWechatBind },
  { title: "通知设置", desc: "提醒和消息偏好后续开放", icon: "铃", color: "orange", action: () => showTodo("通知设置") },
  { title: "隐私政策", desc: "查看隐私保护说明", icon: "隐", color: "gray", action: () => showTodo("隐私政策") },
  { title: "用户协议", desc: "查看平台使用协议", icon: "协", color: "gray", action: () => showTodo("用户协议") },
  { title: "关于我们", desc: "宠护星球版本信息", icon: "星", color: "blue", action: () => showTodo("关于我们") },
];

onShow(async () => {
  if (!authStore.isLoggedIn) {
    resetSummary();
    return;
  }
  try {
    await authStore.fetchMe();
    await fetchSummary();
  } catch (error) {
    authStore.clearAuth();
    resetSummary();
  }
});

async function fetchSummary() {
  const response = await getUserSummary();
  Object.assign(summary, response.data);
}

function resetSummary() {
  Object.assign(summary, {
    pet_count: 0,
    ai_conversation_count: 0,
    pending_action_count: 0,
    has_wechat_bound: false,
  });
}

function goAuth() {
  uni.navigateTo({ url: "/pages/auth/index" });
}

function goPets() {
  if (!isLoggedIn.value) {
    goAuth();
    return;
  }
  uni.switchTab({ url: "/pages/pets/index" });
}

function goAi() {
  if (!isLoggedIn.value) {
    goAuth();
    return;
  }
  uni.switchTab({ url: "/pages/ai/index" });
}

function showTodo(name: string) {
  uni.showToast({ title: `${name}功能开发中`, icon: "none" });
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
      nickname: user.value?.nickname || "微信用户",
      avatar: user.value?.avatar || "",
    });
    authStore.setAuth(response.data);
    await fetchSummary();
    uni.showToast({ title: "登录成功", icon: "success" });
  } catch (error) {
    const message = (error as { message?: string })?.message || "微信登录失败，请稍后再试";
    uni.showToast({ title: message, icon: "none" });
  }
}

function handleWechatBind() {
  if (!isLoggedIn.value) {
    goAuth();
    return;
  }
  if (user.value?.has_wechat_bound) {
    uni.showToast({ title: "已绑定微信", icon: "none" });
    return;
  }
  if (isMiniApp.value) {
    handleWechatLogin(false);
    return;
  }
  if (isDevMode) {
    handleWechatLogin(true);
    return;
  }
  uni.showToast({ title: "微信登录待配置", icon: "none" });
}

function confirmLogout() {
  uni.showModal({
    title: "退出登录",
    content: "确定要退出当前账号吗？",
    confirmText: "退出",
    confirmColor: "#f05a28",
    success: async (result) => {
      if (!result.confirm) {
        return;
      }
      await handleLogout();
    },
  });
}

async function handleLogout() {
  try {
    await logout();
  } catch (error) {
    // Local logout still clears client state if the server request fails.
  }
  authStore.clearAuth();
  resetSummary();
  uni.switchTab({ url: "/pages/index/index" });
}
</script>

<style scoped>
.user-page {
  min-height: 100vh;
  padding: 44rpx 30rpx calc(132rpx + env(safe-area-inset-bottom));
  box-sizing: border-box;
  background:
    radial-gradient(circle at 88% 8%, rgba(255, 213, 155, 0.24), transparent 190rpx),
    radial-gradient(circle at 6% 0%, rgba(174, 224, 255, 0.76), transparent 260rpx),
    linear-gradient(180deg, #eef8ff 0%, #f8fcff 100%);
  overflow-x: hidden;
}

.page-header {
  padding: 20rpx 4rpx 22rpx;
}

.page-title {
  display: block;
  color: #10172d;
  font-size: 42rpx;
  font-weight: 850;
  line-height: 1.2;
}

.page-subtitle {
  display: block;
  margin-top: 10rpx;
  color: #64748b;
  font-size: 25rpx;
  line-height: 1.35;
}

.profile-card,
.stats-card,
.section-card {
  border: 1rpx solid rgba(216, 232, 247, 0.82);
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 22rpx;
  padding: 28rpx;
}

.avatar {
  flex: 0 0 auto;
  width: 126rpx;
  height: 126rpx;
  border: 8rpx solid #fff;
  border-radius: 999rpx;
  background: #eaf6ff;
  box-shadow: 0 10rpx 26rpx rgba(31, 140, 255, 0.13);
}

.profile-main {
  flex: 1;
  min-width: 0;
}

.nickname {
  display: block;
  color: #10172d;
  font-size: 34rpx;
  font-weight: 850;
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-subtitle {
  display: block;
  margin-top: 10rpx;
  color: #7b879b;
  font-size: 24rpx;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 14rpx;
}

.provider-tag,
.wechat-status {
  max-width: 180rpx;
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #edf6ff;
  color: #1f7eea;
  font-size: 21rpx;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.wechat-status {
  background: #f2f5f8;
  color: #7b879b;
}

.wechat-status.bound {
  background: #edfff5;
  color: #18a45c;
}

.edit-button {
  flex: 0 0 auto;
  min-width: 92rpx;
  height: 58rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: #edf6ff;
  color: #1f8cff;
  font-size: 24rpx;
  font-weight: 800;
}

.login-actions {
  display: grid;
  gap: 18rpx;
  margin-top: 22rpx;
}

.primary-button,
.wechat-button,
.logout-button {
  height: 84rpx;
  border-radius: 999rpx;
  font-size: 28rpx;
  font-weight: 850;
  line-height: 84rpx;
}

.primary-button {
  background: linear-gradient(135deg, #1476ff, #1f8cff);
  color: #fff;
  box-shadow: 0 16rpx 30rpx rgba(31, 140, 255, 0.22);
}

.wechat-button {
  border: 1rpx solid #bfe8d4;
  background: #f2fff8;
  color: #19a35b;
}

.wechat-button.mock {
  border-color: #cde7ff;
  background: #f3f9ff;
  color: #1f8cff;
}

.stats-card {
  display: grid;
  grid-template-columns: 1fr 1rpx 1fr 1rpx 1fr;
  align-items: center;
  margin-top: 22rpx;
  padding: 24rpx 8rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
}

.stat-number {
  color: #10172d;
  font-size: 38rpx;
  font-weight: 900;
  line-height: 1;
}

.stat-number.accent {
  color: #1f8cff;
}

.stat-label {
  margin-top: 12rpx;
  color: #718096;
  font-size: 23rpx;
  font-weight: 650;
}

.stat-divider {
  height: 58rpx;
  background: #edf2f7;
}

.section-card {
  margin-top: 24rpx;
  padding: 22rpx 24rpx 8rpx;
}

.section-title {
  margin-bottom: 6rpx;
  color: #10172d;
  font-size: 30rpx;
  font-weight: 850;
}

.menu-row {
  display: flex;
  align-items: center;
  min-height: 92rpx;
  gap: 18rpx;
  border-bottom: 1rpx solid #edf3f8;
}

.menu-row:last-child {
  border-bottom: 0;
}

.menu-icon {
  flex: 0 0 auto;
  width: 54rpx;
  height: 54rpx;
  border-radius: 18rpx;
  color: #1f8cff;
  font-size: 22rpx;
  font-weight: 900;
  line-height: 54rpx;
  text-align: center;
}

.menu-icon.blue {
  background: #edf6ff;
  color: #1f8cff;
}

.menu-icon.green {
  background: #edfff5;
  color: #18a45c;
}

.menu-icon.orange {
  background: #fff6eb;
  color: #f59e0b;
}

.menu-icon.gray {
  background: #f2f5f8;
  color: #718096;
}

.menu-text {
  flex: 1;
  min-width: 0;
}

.menu-title {
  display: block;
  color: #1a2438;
  font-size: 27rpx;
  font-weight: 800;
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-desc {
  display: block;
  margin-top: 6rpx;
  color: #8a95a6;
  font-size: 22rpx;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chevron {
  flex: 0 0 auto;
  color: #a4afbd;
  font-size: 42rpx;
  line-height: 1;
}

.logout-button {
  margin-top: 28rpx;
  background: #fff1ec;
  color: #f05a28;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}

button::after {
  border: 0;
}

@media (max-width: 380px) {
  .user-page {
    padding-left: 24rpx;
    padding-right: 24rpx;
  }

  .nickname {
    font-size: 31rpx;
  }

  .profile-card {
    gap: 18rpx;
    padding: 24rpx;
  }

  .avatar {
    width: 112rpx;
    height: 112rpx;
  }
}
</style>

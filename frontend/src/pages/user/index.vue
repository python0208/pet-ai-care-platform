<template>
  <view class="user-page">
    <view class="profile-card">
      <image
        class="avatar"
        :src="user?.avatar || '/static/images/default-user-avatar.svg'"
        mode="aspectFill"
      />
      <view class="profile-info">
        <text class="nickname">{{ user?.nickname || "宠护用户" }}</text>
        <text class="email">{{ user?.email || "" }}</text>
      </view>
    </view>

    <view class="menu-card">
      <view class="menu-row">
        <text>邮箱状态</text>
        <text class="muted">{{ user?.is_email_verified ? "已验证" : "当前 MVP 不使用邮箱验证" }}</text>
      </view>
      <view class="menu-row tappable" @tap="goPets">
        <text>我的宠物</text>
        <text class="muted">查看档案</text>
      </view>
      <view class="menu-row">
        <text>资料设置</text>
        <text class="muted">{{ genderLabel }}</text>
      </view>
    </view>

    <button class="logout-button" hover-class="button-tap" @tap="handleLogout">退出登录</button>
  </view>
</template>

<script setup lang="ts">
import { onShow } from "@dcloudio/uni-app";
import { computed } from "vue";

import { logout } from "@/api/auth";
import { useAuthStore } from "@/stores/auth";
import { requireAuth } from "@/utils/auth";

const authStore = useAuthStore();
const user = computed(() => authStore.user);
const genderLabel = computed(() => {
  if (user.value?.gender === "male") {
    return "男";
  }
  if (user.value?.gender === "female") {
    return "女";
  }
  return "未知";
});

onShow(async () => {
  if (!requireAuth()) {
    return;
  }
  try {
    await authStore.fetchMe();
  } catch (error) {
    authStore.clearAuth();
    uni.navigateTo({ url: "/pages/auth/index" });
  }
});

async function handleLogout() {
  try {
    await logout();
  } catch (error) {
    // Local logout still clears client state if the server request fails.
  }
  authStore.clearAuth();
  uni.switchTab({ url: "/pages/index/index" });
}

function goPets() {
  uni.switchTab({ url: "/pages/pets/index" });
}
</script>

<style scoped>
.user-page {
  min-height: 100vh;
  padding: 88rpx 30rpx 48rpx;
  background:
    radial-gradient(circle at 88% 8%, rgba(255, 213, 155, 0.28), transparent 200rpx),
    linear-gradient(180deg, #eef8ff 0%, #fbfdff 100%);
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 30rpx;
  border-radius: 36rpx;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.12);
}

.avatar {
  width: 132rpx;
  height: 132rpx;
  border: 8rpx solid #fff;
  border-radius: 999rpx;
  background: #eaf6ff;
  box-shadow: 0 10rpx 26rpx rgba(31, 140, 255, 0.12);
}

.profile-info {
  flex: 1;
  min-width: 0;
}

.nickname {
  display: block;
  color: #10172d;
  font-size: 38rpx;
  font-weight: 900;
  line-height: 1.25;
}

.email {
  display: block;
  margin-top: 12rpx;
  color: #7d8799;
  font-size: 26rpx;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.menu-card {
  margin-top: 26rpx;
  padding: 8rpx 26rpx;
  border-radius: 30rpx;
  background: #fff;
  box-shadow: 0 12rpx 36rpx rgba(30, 119, 188, 0.08);
}

.menu-row {
  min-height: 92rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1rpx solid #eef3f8;
  color: #17213a;
  font-size: 28rpx;
  font-weight: 800;
}

.menu-row:last-child {
  border-bottom: 0;
}

.tappable {
  cursor: pointer;
}

.muted {
  max-width: 360rpx;
  color: #7d8799;
  font-size: 24rpx;
  font-weight: 500;
  text-align: right;
}

.logout-button {
  height: 88rpx;
  margin-top: 34rpx;
  border-radius: 999rpx;
  background: #fff1ec;
  color: #f05a28;
  font-size: 30rpx;
  font-weight: 900;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

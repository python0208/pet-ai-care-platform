<template>
  <scroll-view class="ai-page" scroll-y>
    <view class="page-inner">
      <view class="hero-row">
        <view>
          <view class="title-row">
            <text class="page-title">AI养宠助手</text>
            <image src="/static/icons/png/ai_robot.png" mode="aspectFit" />
          </view>
          <text class="page-subtitle">结合宠物档案，回答养护问题，整理待确认记录</text>
        </view>
      </view>

      <view class="notice-card">
        <text>健康相关建议仅供养宠护理参考，不能替代专业兽医诊断。</text>
      </view>

      <view v-if="loading" class="state-card">
        <image src="/static/icons/png/ai_robot.png" mode="aspectFit" />
        <text>正在准备咨询入口...</text>
      </view>

      <view v-else-if="errorMessage" class="state-card">
        <image src="/static/icons/archive/empty_pet.png" mode="aspectFit" />
        <text>{{ errorMessage }}</text>
        <button class="primary-button" hover-class="button-tap" @tap="loadPageData">重新加载</button>
      </view>

      <view v-else-if="pets.length === 0" class="empty-card">
        <image src="/static/icons/archive/empty_pet.png" mode="aspectFit" />
        <text class="empty-title">还没有宠物档案</text>
        <text class="empty-text">请先为毛孩子建立档案，再进行 AI 健康咨询</text>
        <button class="primary-button" hover-class="button-tap" @tap="goCreatePet">去添加宠物</button>
      </view>

      <template v-else>
        <view class="pet-panel">
          <view class="section-head">
            <text class="section-title">选择咨询对象</text>
            <text class="section-sub">{{ selectedPet?.name || "请选择" }}</text>
          </view>
          <scroll-view class="pet-switcher" scroll-x :show-scrollbar="false">
            <view class="pet-switch-track">
              <view
                v-for="pet in pets"
                :key="pet.id"
                class="pet-switch-item"
                :class="{ active: pet.id === selectedPetId }"
                @tap="selectPet(pet.id)"
              >
                <image :src="petAvatarUrl(pet.avatar)" mode="aspectFill" />
                <text>{{ pet.name }}</text>
              </view>
            </view>
          </scroll-view>
          <button class="consult-button" hover-class="button-tap" @tap="startConsult">开始咨询</button>
        </view>

        <view class="quick-card">
          <view class="section-head">
            <text class="section-title">快捷问题</text>
          </view>
          <view v-for="group in quickGroups" :key="group.title" class="quick-group">
            <text class="quick-group-title">{{ group.title }}</text>
            <view class="quick-list">
              <view
                v-for="item in group.items"
                :key="item"
                class="quick-chip"
                @tap="startConsult(item)"
              >
                <text>{{ item }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="history-card">
          <view class="section-head">
            <text class="section-title">历史咨询</text>
          </view>
          <view v-if="conversations.length === 0" class="soft-empty">暂无咨询记录</view>
          <view v-else class="conversation-list">
            <view
              v-for="conversation in conversations"
              :key="conversation.id"
              class="conversation-row"
              @tap="openConversation(conversation)"
            >
              <view class="conversation-main">
                <text class="conversation-title">{{ conversation.title }}</text>
                <text class="conversation-sub">{{ conversation.pet_name || "宠物" }}｜{{ dateLabel(conversation.updated_at) }}</text>
              </view>
              <text class="row-arrow">›</text>
            </view>
          </view>
        </view>
      </template>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { onShow } from "@dcloudio/uni-app";
import { computed, ref } from "vue";

import { getConversations } from "@/api/ai";
import { getPets } from "@/api/pets";
import { resolveMediaUrl } from "@/api/request";
import type { AIConversation } from "@/types/ai";
import type { Pet } from "@/types/pet";
import { requireAuth } from "@/utils/auth";

const SELECTED_PET_STORAGE_KEY = "selected_pet_id";

const loading = ref(false);
const errorMessage = ref("");
const pets = ref<Pet[]>([]);
const conversations = ref<AIConversation[]>([]);
const selectedPetId = ref<number | null>(null);

const quickGroups = [
  { title: "健康咨询", items: ["呕吐怎么办", "拉稀怎么办", "不吃饭怎么办", "皮肤瘙痒怎么办"] },
  { title: "日常养护", items: ["今天吃多少合适？", "怎么给猫换粮？", "多久洗一次澡？", "晚上太活跃怎么办？"] },
  { title: "档案记录", items: ["记录豆豆今天体重 4.8kg", "记录今天做了体外驱虫", "记录今天接种了疫苗", "记录豆豆对鸡肉过敏"] },
];

const selectedPet = computed(() => pets.value.find((pet) => pet.id === selectedPetId.value) || null);

onShow(async () => {
  if (!requireAuth()) {
    return;
  }
  await loadPageData();
});

async function loadPageData() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const [petResponse, conversationResponse] = await Promise.all([
      getPets(),
      getConversations(),
    ]);
    pets.value = petResponse.data;
    conversations.value = conversationResponse.data;
    if (pets.value.length > 0) {
      const savedPetId = Number(uni.getStorageSync(SELECTED_PET_STORAGE_KEY));
      selectedPetId.value = pets.value.some((pet) => pet.id === savedPetId)
        ? savedPetId
        : pets.value[0].id;
      uni.setStorageSync(SELECTED_PET_STORAGE_KEY, String(selectedPetId.value));
    }
  } catch (error) {
    errorMessage.value = "AI 咨询入口加载失败，请稍后重试";
  } finally {
    loading.value = false;
  }
}

function selectPet(id: number) {
  selectedPetId.value = id;
  uni.setStorageSync(SELECTED_PET_STORAGE_KEY, String(id));
}

function startConsult(question?: string) {
  if (!selectedPetId.value) {
    return;
  }
  const query = [`petId=${selectedPetId.value}`];
  if (typeof question === "string" && question) {
    query.push(`question=${encodeURIComponent(question)}`);
  }
  uni.navigateTo({ url: `/pages/ai/chat?${query.join("&")}` });
}

function openConversation(conversation: AIConversation) {
  const petId = conversation.pet || selectedPetId.value;
  const query = [`conversationId=${conversation.id}`];
  if (petId) {
    query.push(`petId=${petId}`);
  }
  uni.navigateTo({ url: `/pages/ai/chat?${query.join("&")}` });
}

function goCreatePet() {
  uni.navigateTo({ url: "/pages/pets/edit" });
}

function petAvatarUrl(avatar: string) {
  return resolveMediaUrl(avatar) || "/static/images/default-pet-avatar.svg";
}

function dateLabel(value: string) {
  return value ? value.slice(0, 10) : "";
}
</script>

<style scoped>
.ai-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 0% 12%, rgba(218, 239, 255, 0.9), transparent 270rpx),
    radial-gradient(circle at 100% 28%, rgba(230, 247, 255, 0.92), transparent 260rpx),
    linear-gradient(180deg, #eff8ff 0%, #fbfdff 58%, #ffffff 100%);
}

.page-inner {
  min-height: 100vh;
  padding: 52rpx 30rpx 58rpx;
  box-sizing: border-box;
}

.hero-row,
.title-row,
.section-head {
  display: flex;
  align-items: center;
}

.hero-row {
  justify-content: space-between;
}

.title-row {
  gap: 12rpx;
}

.title-row image {
  width: 58rpx;
  height: 58rpx;
}

.page-title {
  color: #10172d;
  font-size: 52rpx;
  font-weight: 900;
  line-height: 1.12;
}

.page-subtitle {
  display: block;
  max-width: 620rpx;
  margin-top: 12rpx;
  color: #637086;
  font-size: 27rpx;
  line-height: 1.5;
}

.notice-card,
.state-card,
.empty-card,
.pet-panel,
.quick-card,
.history-card {
  margin-top: 28rpx;
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
}

.notice-card {
  padding: 22rpx 26rpx;
  color: #486079;
  font-size: 24rpx;
  line-height: 1.5;
  background: rgba(235, 247, 255, 0.95);
}

.state-card,
.empty-card {
  padding: 54rpx 34rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.state-card image,
.empty-card image {
  width: 168rpx;
  height: 168rpx;
}

.state-card text,
.empty-text,
.soft-empty {
  color: #7d8799;
  font-size: 26rpx;
  line-height: 1.6;
}

.empty-title {
  margin-top: 20rpx;
  color: #10172d;
  font-size: 34rpx;
  font-weight: 900;
}

.empty-text {
  margin-top: 12rpx;
}

.primary-button,
.consult-button {
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1f8cff, #1268ff);
  color: #fff;
  font-weight: 900;
  box-shadow: 0 16rpx 32rpx rgba(31, 140, 255, 0.24);
}

.primary-button {
  width: 240rpx;
  height: 82rpx;
  margin-top: 28rpx;
  font-size: 28rpx;
}

.pet-panel,
.quick-card,
.history-card {
  padding: 26rpx;
}

.section-head {
  justify-content: space-between;
  gap: 18rpx;
  margin-bottom: 22rpx;
}

.section-title {
  color: #10172d;
  font-size: 34rpx;
  font-weight: 900;
  line-height: 1.2;
}

.section-sub {
  max-width: 220rpx;
  color: #1f8cff;
  font-size: 25rpx;
  font-weight: 900;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.pet-switcher {
  width: 100%;
  white-space: nowrap;
}

.pet-switch-track {
  display: inline-flex;
  gap: 22rpx;
  padding: 4rpx 0 10rpx;
}

.pet-switch-item {
  width: 118rpx;
  flex: 0 0 118rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.pet-switch-item image {
  width: 92rpx;
  height: 92rpx;
  border-radius: 999rpx;
  background: #eef8ff;
  box-sizing: border-box;
}

.pet-switch-item.active image {
  border: 6rpx solid #1f8cff;
  box-shadow: 0 12rpx 26rpx rgba(31, 140, 255, 0.22);
}

.pet-switch-item text {
  width: 100%;
  color: #7d8799;
  font-size: 23rpx;
  font-weight: 800;
  text-align: center;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.pet-switch-item.active text {
  color: #1f8cff;
}

.consult-button {
  width: 100%;
  height: 88rpx;
  margin-top: 18rpx;
  font-size: 30rpx;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.quick-group {
  margin-top: 16rpx;
}

.quick-group-title {
  display: block;
  margin-bottom: 12rpx;
  color: #10172d;
  font-size: 24rpx;
  font-weight: 900;
}

.quick-chip {
  padding: 18rpx 24rpx;
  border-radius: 999rpx;
  background: #f0f8ff;
  color: #1f5fbf;
  font-size: 25rpx;
  font-weight: 900;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.conversation-row {
  min-height: 104rpx;
  padding: 20rpx;
  border: 1rpx solid #edf2f7;
  border-radius: 24rpx;
  background: #fff;
  display: flex;
  align-items: center;
  gap: 18rpx;
  box-sizing: border-box;
}

.conversation-main {
  flex: 1;
  min-width: 0;
}

.conversation-title,
.conversation-sub {
  display: block;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.conversation-title {
  color: #10172d;
  font-size: 28rpx;
  font-weight: 900;
}

.conversation-sub {
  margin-top: 8rpx;
  color: #7d8799;
  font-size: 23rpx;
}

.row-arrow {
  color: #9aa6b8;
  font-size: 42rpx;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

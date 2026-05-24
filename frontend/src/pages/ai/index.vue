<template>
  <scroll-view class="ai-page" scroll-y :show-scrollbar="false">
    <view class="page-inner">
      <view class="hero-card">
        <image class="paw-accent" :src="aiIcon('paw_accent')" mode="aspectFit" />
        <view class="hero-copy">
          <view class="title-row">
            <text class="page-title">AI养宠助手</text>
            <image class="title-bot" :src="aiIcon('ai_robot')" mode="aspectFit" />
          </view>
          <text class="page-subtitle">结合宠物档案，回答养护问题，整理待确认记录</text>
        </view>
        <image class="hero-bot" :src="aiIcon('demo')" mode="aspectFit" />
      </view>

      <view class="notice-pill">
        <image :src="aiIcon('shield_notice')" mode="aspectFit" />
        <text>健康相关建议仅供养宠护理参考，不能替代专业兽医诊断。</text>
      </view>

      <view v-if="loading" class="state-card">
        <image :src="aiIcon('demo')" mode="aspectFit" />
        <text>正在准备咨询入口...</text>
      </view>

      <view v-else-if="errorMessage" class="state-card">
        <image :src="aiIcon('history_question')" mode="aspectFit" />
        <text>{{ errorMessage }}</text>
        <button class="primary-button" hover-class="button-tap" @tap="loadPageData">重新加载</button>
      </view>

      <view v-else-if="pets.length === 0" class="empty-card">
        <image :src="aiIcon('pet_avatar_placeholder')" mode="aspectFit" />
        <text class="empty-title">还没有宠物档案</text>
        <text class="empty-text">请先为毛孩子建立档案，再进行 AI 健康咨询</text>
        <button class="primary-button" hover-class="button-tap" @tap="goCreatePet">去添加宠物</button>
      </view>

      <template v-else>
        <view class="pet-card">
          <view class="card-head">
            <text class="card-title">选择咨询对象</text>
            <view class="current-pet" @tap="goCreatePet">
              <text>当前宠物：{{ selectedPet?.name || "请选择" }}</text>
              <image :src="aiIcon('chevron_right')" mode="aspectFit" />
            </view>
          </view>
          <scroll-view class="pet-switcher" scroll-x :show-scrollbar="false">
            <view class="pet-track">
              <view
                v-for="pet in pets"
                :key="pet.id"
                class="pet-item"
                :class="{ active: pet.id === selectedPetId }"
                @tap="selectPet(pet.id)"
              >
                <view class="avatar-wrap">
                  <image class="pet-avatar" :src="petAvatarUrl(pet.avatar)" mode="aspectFill" />
                  <image
                    v-if="pet.id === selectedPetId"
                    class="check-icon"
                    :src="aiIcon('pet_selected_check')"
                    mode="aspectFit"
                  />
                </view>
                <text>{{ pet.name }}</text>
              </view>
              <view class="pet-item add-pet" @tap="goCreatePet">
                <view class="avatar-wrap add-wrap">
                  <image class="add-icon" :src="aiIcon('add_pet_plus')" mode="aspectFit" />
                </view>
                <text>添加</text>
              </view>
            </view>
          </scroll-view>
        </view>

        <view class="quick-card">
          <view class="card-head">
            <text class="card-title">快捷问题</text>
            <view class="view-all" @tap="cycleQuickGroup">
              <text>查看全部</text>
              <image :src="aiIcon('view_all')" mode="aspectFit" />
            </view>
          </view>

          <view class="quick-tabs">
            <view
              v-for="(group, index) in quickGroups"
              :key="group.title"
              class="quick-tab"
              :class="{ active: activeQuickIndex === index }"
              @tap="activeQuickIndex = index"
            >
              <image :src="aiIcon(group.icon)" mode="aspectFit" />
              <text>{{ group.title }}</text>
            </view>
          </view>

          <view class="quick-chip-grid">
            <view
              v-for="item in activeQuickItems"
              :key="item"
              class="quick-chip"
              hover-class="button-tap"
              @tap="startConsult(item)"
            >
              <text>{{ item }}</text>
            </view>
          </view>

          <view class="ask-entry" hover-class="button-tap" @tap="startConsult()">
            <image class="input-bot" :src="aiIcon('input_bot')" mode="aspectFit" />
            <text class="ask-placeholder">问养宠问题，或记录体重 4.8kg</text>
            <button class="start-button" hover-class="button-tap" @tap.stop="startConsult()">开始咨询</button>
          </view>
        </view>

        <view class="history-card">
          <view class="card-head">
            <text class="card-title">历史咨询</text>
            <view class="view-all" @tap="noop">
              <text>查看全部</text>
              <image :src="aiIcon('view_all')" mode="aspectFit" />
            </view>
          </view>
          <view v-if="conversations.length === 0" class="soft-empty">
            <image :src="aiIcon('history_question')" mode="aspectFit" />
            <text>还没有咨询记录</text>
            <text>试着问一个养宠问题吧</text>
          </view>
          <view v-else class="conversation-list">
            <view
              v-for="conversation in conversations"
              :key="conversation.id"
              class="conversation-row"
              hover-class="button-tap"
              @tap="openConversation(conversation)"
            >
              <image class="history-icon" :src="historyIcon(conversation)" mode="aspectFit" />
              <view class="conversation-main">
                <text class="conversation-title">{{ conversation.title || "AI养宠咨询" }}</text>
                <text class="conversation-sub">{{ conversation.pet_name || "宠物" }}｜{{ dateLabel(conversation.updated_at) }}</text>
              </view>
              <view class="conversation-right">
                <view class="mode-tag" :class="{ draft: isDraftConversation(conversation) }">
                  <image :src="aiIcon(isDraftConversation(conversation) ? 'tag_draft' : 'tag_health')" mode="aspectFit" />
                  <text>{{ conversationTag(conversation) }}</text>
                </view>
                <text v-if="conversation.pending_action_count" class="pending-text">有待确认记录</text>
              </view>
              <image class="chevron" :src="aiIcon('chevron_right')" mode="aspectFit" />
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
const activeQuickIndex = ref(0);

const quickGroups = [
  { title: "健康咨询", icon: "quick_health", items: ["呕吐怎么办", "拉稀怎么办", "不吃饭怎么办", "皮肤瘙痒怎么办"] },
  { title: "日常养护", icon: "quick_daily_care", items: ["今天吃多少合适？", "怎么给猫换粮？", "多久洗一次澡？", "晚上太活跃怎么办？"] },
  { title: "档案记录", icon: "quick_archive", items: ["记录今天体重 4.8kg", "记录今天做了体外驱虫", "记录今天接种了疫苗", "记录对鸡肉过敏"] },
];

const selectedPet = computed(() => pets.value.find((pet) => pet.id === selectedPetId.value) || null);
const activeQuickItems = computed(() => quickGroups[activeQuickIndex.value]?.items || []);

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
  if (pets.value.length === 0) {
    uni.showToast({ title: "请先添加宠物档案", icon: "none" });
    return;
  }
  if (!selectedPetId.value) {
    uni.showToast({ title: "请先选择宠物", icon: "none" });
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

function cycleQuickGroup() {
  activeQuickIndex.value = (activeQuickIndex.value + 1) % quickGroups.length;
}

function noop() {}

function petAvatarUrl(avatar: string) {
  return resolveMediaUrl(avatar) || aiIcon("pet_avatar_placeholder");
}

function dateLabel(value: string) {
  return value ? value.slice(0, 10) : "";
}

function aiIcon(name: string) {
  return `/static/icons/ai/${name}.png`;
}

function isDraftConversation(conversation: AIConversation) {
  const title = conversation.title || "";
  return Boolean(conversation.pending_action_count) || /记录|体重|疫苗|驱虫|过敏/.test(title);
}

function conversationTag(conversation: AIConversation) {
  if (isDraftConversation(conversation)) {
    return conversation.pending_action_count ? "记录草稿" : "健康咨询";
  }
  if (/换粮|洗澡|吃多少|活跃|行为|新手|养护/.test(conversation.title || "")) {
    return "日常养护";
  }
  return "健康咨询";
}

function historyIcon(conversation: AIConversation) {
  const title = conversation.title || "";
  if (/驱虫/.test(title)) {
    return aiIcon("history_deworm");
  }
  if (/疫苗|接种/.test(title)) {
    return aiIcon("history_vaccine");
  }
  if (/皮肤|瘙痒|痒/.test(title)) {
    return aiIcon("history_skin");
  }
  return aiIcon("history_question");
}
</script>

<style scoped>
.ai-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 2% 12%, rgba(218, 239, 255, 0.9), transparent 260rpx),
    radial-gradient(circle at 100% 28%, rgba(230, 247, 255, 0.9), transparent 260rpx),
    linear-gradient(180deg, #eff8ff 0%, #fbfdff 58%, #ffffff 100%);
}

.page-inner {
  min-height: 100vh;
  padding: 26rpx 24rpx calc(190rpx + env(safe-area-inset-bottom));
  box-sizing: border-box;
  overflow-x: hidden;
}

.hero-card {
  position: relative;
  min-height: 206rpx;
  padding: 30rpx 260rpx 24rpx 0;
  box-sizing: border-box;
  overflow: hidden;
}

.hero-copy {
  position: relative;
  z-index: 2;
  min-width: 0;
}

.title-row,
.card-head,
.current-pet,
.view-all,
.quick-tab,
.ask-entry,
.conversation-row,
.conversation-right,
.mode-tag {
  display: flex;
  align-items: center;
}

.title-row {
  gap: 10rpx;
}

.page-title {
  color: #10172d;
  font-size: 54rpx;
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: 0;
}

.title-bot {
  width: 44rpx;
  height: 44rpx;
}

.page-subtitle {
  display: block;
  margin-top: 16rpx;
  color: #66758e;
  font-size: 27rpx;
  line-height: 1.4;
}

.hero-bot {
  position: absolute;
  right: 4rpx;
  top: 12rpx;
  width: 240rpx;
  height: 180rpx;
  z-index: 1;
}

.paw-accent {
  position: absolute;
  right: 190rpx;
  top: 10rpx;
  width: 54rpx;
  height: 54rpx;
  opacity: 0.32;
}

.notice-pill,
.pet-card,
.quick-card,
.history-card,
.state-card,
.empty-card {
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.09);
}

.notice-pill {
  min-height: 72rpx;
  padding: 12rpx 22rpx;
  border: 2rpx solid rgba(160, 206, 255, 0.72);
  background: rgba(239, 248, 255, 0.78);
  color: #1f6fda;
  font-size: 25rpx;
  line-height: 1.35;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.notice-pill image {
  width: 34rpx;
  height: 34rpx;
  flex: 0 0 34rpx;
}

.pet-card,
.quick-card,
.history-card {
  margin-top: 24rpx;
  padding: 28rpx 26rpx;
  box-sizing: border-box;
}

.card-head {
  justify-content: space-between;
  gap: 18rpx;
  margin-bottom: 24rpx;
}

.card-title {
  color: #10172d;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1.2;
}

.current-pet,
.view-all {
  flex: 0 0 auto;
  max-width: 320rpx;
  gap: 8rpx;
  color: #6c7890;
  font-size: 24rpx;
  font-weight: 700;
}

.current-pet text {
  min-width: 0;
  color: #6c7890;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.current-pet text::first-letter {
  color: #6c7890;
}

.current-pet image,
.view-all image,
.chevron {
  width: 28rpx;
  height: 28rpx;
  flex: 0 0 28rpx;
}

.view-all {
  color: #7b8495;
  font-weight: 600;
}

.pet-switcher {
  width: 100%;
  white-space: nowrap;
}

.pet-track {
  display: inline-flex;
  gap: 44rpx;
  padding: 2rpx 10rpx 4rpx;
}

.pet-item {
  width: 108rpx;
  flex: 0 0 108rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.avatar-wrap {
  position: relative;
  width: 90rpx;
  height: 90rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.pet-avatar {
  width: 86rpx;
  height: 86rpx;
  border-radius: 999rpx;
  background: #eef8ff;
}

.pet-item.active .avatar-wrap {
  border: 5rpx solid #1f8cff;
  box-shadow: 0 10rpx 24rpx rgba(31, 140, 255, 0.2);
}

.check-icon {
  position: absolute;
  right: -8rpx;
  bottom: 0;
  width: 34rpx;
  height: 34rpx;
}

.add-wrap {
  border: 2rpx dashed #c2d4e8;
}

.add-icon {
  width: 42rpx;
  height: 42rpx;
}

.pet-item text {
  width: 100%;
  color: #788398;
  font-size: 24rpx;
  font-weight: 700;
  text-align: center;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.pet-item.active text {
  color: #1f8cff;
}

.quick-tabs {
  height: 78rpx;
  padding: 6rpx;
  border: 2rpx solid #e7f0fb;
  border-radius: 28rpx;
  background: #fbfdff;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.quick-tab {
  flex: 1;
  height: 64rpx;
  justify-content: center;
  gap: 8rpx;
  border-radius: 24rpx;
  color: #6b7486;
  font-size: 25rpx;
  font-weight: 700;
  box-sizing: border-box;
}

.quick-tab image {
  width: 30rpx;
  height: 30rpx;
}

.quick-tab.active {
  background: linear-gradient(135deg, #1f8cff, #1268ff);
  color: #fff;
  box-shadow: 0 12rpx 26rpx rgba(31, 140, 255, 0.2);
}

.quick-chip-grid {
  margin-top: 22rpx;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx 20rpx;
}

.quick-chip {
  min-width: 0;
  height: 62rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: #f0f8ff;
  color: #1f68d8;
  font-size: 25rpx;
  font-weight: 700;
  line-height: 62rpx;
  box-sizing: border-box;
}

.quick-chip text {
  display: block;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  text-align: center;
}

.ask-entry {
  min-height: 84rpx;
  margin-top: 24rpx;
  padding: 10rpx 12rpx 10rpx 16rpx;
  border: 2rpx solid #cfe5ff;
  border-radius: 28rpx;
  background: #ffffff;
  gap: 14rpx;
  box-sizing: border-box;
  box-shadow: inset 0 0 0 4rpx rgba(231, 243, 255, 0.7);
}

.input-bot {
  width: 50rpx;
  height: 50rpx;
  flex: 0 0 50rpx;
}

.ask-placeholder {
  flex: 1;
  min-width: 0;
  color: #6c7890;
  font-size: 25rpx;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.start-button {
  width: 152rpx;
  height: 62rpx;
  flex: 0 0 152rpx;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1f8cff, #1268ff);
  color: #fff;
  font-size: 25rpx;
  font-weight: 800;
  line-height: 62rpx;
  white-space: nowrap;
  box-shadow: 0 12rpx 26rpx rgba(31, 140, 255, 0.22);
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.conversation-row {
  min-height: 92rpx;
  padding: 14rpx 16rpx;
  border: 1rpx solid #e8eef6;
  border-radius: 24rpx;
  background: #fff;
  gap: 16rpx;
  box-sizing: border-box;
}

.history-icon {
  width: 62rpx;
  height: 62rpx;
  flex: 0 0 62rpx;
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
  font-size: 27rpx;
  font-weight: 800;
  line-height: 1.25;
}

.conversation-sub {
  margin-top: 8rpx;
  color: #6f7b91;
  font-size: 23rpx;
  line-height: 1.2;
}

.conversation-right {
  flex: 0 0 auto;
  align-items: flex-end;
  flex-direction: column;
  gap: 6rpx;
}

.mode-tag {
  height: 38rpx;
  padding: 0 12rpx;
  border-radius: 999rpx;
  background: #e9f8ee;
  color: #22b665;
  font-size: 20rpx;
  font-weight: 800;
  gap: 5rpx;
  white-space: nowrap;
}

.mode-tag.draft {
  background: #fff7ed;
  color: #f59e0b;
}

.mode-tag image {
  width: 22rpx;
  height: 22rpx;
}

.pending-text {
  max-width: 144rpx;
  color: #f59e0b;
  font-size: 19rpx;
  font-weight: 700;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.chevron {
  opacity: 0.78;
}

.state-card,
.empty-card {
  margin-top: 24rpx;
  padding: 48rpx 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.state-card image,
.empty-card image {
  width: 142rpx;
  height: 142rpx;
}

.state-card text,
.empty-text,
.soft-empty text {
  color: #7d8799;
  font-size: 25rpx;
  line-height: 1.55;
}

.empty-title,
.empty-text,
.soft-empty text {
  display: block;
}

.empty-title {
  margin-top: 18rpx;
  color: #10172d;
  font-size: 32rpx;
  font-weight: 800;
}

.empty-text {
  margin-top: 10rpx;
}

.primary-button {
  width: 220rpx;
  height: 74rpx;
  margin-top: 24rpx;
  padding: 0;
  border: 0;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1f8cff, #1268ff);
  color: #fff;
  font-size: 26rpx;
  font-weight: 800;
  line-height: 74rpx;
}

.soft-empty {
  padding: 34rpx 0 22rpx;
  text-align: center;
}

.soft-empty image {
  width: 76rpx;
  height: 76rpx;
  margin-bottom: 12rpx;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

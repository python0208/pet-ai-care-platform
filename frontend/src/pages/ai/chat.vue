<template>
  <view class="chat-page">
    <view class="top-bar">
      <button class="back-button" hover-class="button-tap" @tap="goBack">‹</button>
      <view class="top-title">
        <text>AI养宠助手</text>
        <text>{{ selectedPet?.name || "请选择宠物" }}</text>
      </view>
      <view class="top-spacer"></view>
    </view>

    <view class="chat-tools">
      <view class="disclaimer-strip">
        <text>健康建议仅供护理参考，不能替代专业兽医诊断。</text>
      </view>

      <view v-if="pets.length > 0" class="pet-strip">
        <scroll-view scroll-x :show-scrollbar="false">
          <view class="pet-track">
            <view
              v-for="pet in pets"
              :key="pet.id"
              class="pet-chip"
              :class="{ active: pet.id === selectedPetId }"
              @tap="selectPet(pet.id)"
            >
              <image :src="petAvatarUrl(pet.avatar)" mode="aspectFill" />
              <text>{{ pet.name }}</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <view class="quick-panel">
        <scroll-view class="quick-tabs-scroll" scroll-x :show-scrollbar="false">
          <view class="quick-tabs">
            <view
              v-for="(group, index) in quickGroups"
              :key="group.title"
              class="quick-tab"
              :class="{ active: activeQuickIndex === index }"
              @tap="activeQuickIndex = index"
            >
              <text>{{ group.title }}</text>
            </view>
          </view>
        </scroll-view>
        <scroll-view class="quick-chip-scroll" scroll-x :show-scrollbar="false">
          <view class="quick-track">
            <view
              v-for="item in activeQuickItems"
              :key="item"
              class="quick-chip"
              @tap="fillQuestion(item)"
            >
              <text>{{ item }}</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <scroll-view
      class="message-scroll"
      scroll-y
      :scroll-into-view="scrollAnchor"
      :show-scrollbar="false"
    >
      <view class="scroll-inner">
        <view v-if="pets.length === 0" class="empty-card">
          <image src="/static/icons/archive/empty_pet.png" mode="aspectFit" />
          <text class="empty-title">还没有宠物档案</text>
          <text class="empty-text">请先为毛孩子建立档案，再进行 AI 咨询</text>
          <button class="save-button empty-button" hover-class="button-tap" @tap="goCreatePet">去添加宠物</button>
        </view>

        <view v-else class="messages">
          <view v-for="item in localMessages" :key="item.id" class="message-item" :class="item.role">
            <view class="bubble">
              <text v-if="item.content">{{ item.content }}</text>
              <view v-if="item.imageUrls.length > 0" class="bubble-images">
                <view v-for="url in item.imageUrls" :key="url" class="message-image-wrap">
                  <image
                    v-if="!isImageFailed(url)"
                    class="message-image"
                    :src="mediaUrl(url)"
                    mode="aspectFill"
                    @error="markImageError(url)"
                    @tap="previewImage(url, item.imageUrls)"
                  />
                  <text v-else class="image-fallback">图片加载失败</text>
                </view>
              </view>
            </view>

            <view v-if="item.result" class="result-card">
              <view class="risk-row">
                <text class="risk-pill" :class="item.result.risk_level">{{ riskLabel(item.result.risk_level) }}</text>
                <text class="vet-flag">{{ item.result.need_vet ? "建议联系线下宠物医院" : "可先观察护理" }}</text>
              </view>
              <view v-if="item.result.summary" class="result-section">
                <text class="result-title">症状总结</text>
                <text class="result-text">{{ item.result.summary }}</text>
              </view>
              <view v-if="item.result.possible_causes.length" class="result-section">
                <text class="result-title">可能原因</text>
                <text v-for="cause in item.result.possible_causes" :key="cause" class="list-line">· {{ cause }}</text>
              </view>
              <view v-if="item.result.home_care.length" class="result-section">
                <text class="result-title">家庭护理建议</text>
                <text v-for="care in item.result.home_care" :key="care" class="list-line">· {{ care }}</text>
              </view>
              <view v-if="item.result.warning_signs.length" class="result-section">
                <text class="result-title">危险信号</text>
                <text v-for="sign in item.result.warning_signs" :key="sign" class="list-line">· {{ sign }}</text>
              </view>
              <view v-if="item.result.questions_to_ask.length" class="result-section">
                <text class="result-title">建议补充问题</text>
                <text v-for="question in item.result.questions_to_ask" :key="question" class="list-line">· {{ question }}</text>
              </view>
              <view v-if="item.result.disclaimer" class="result-disclaimer">
                <text>{{ item.result.disclaimer }}</text>
              </view>
            </view>

            <view
              v-for="draft in item.actionDrafts"
              :key="draft.id"
              class="draft-card"
              :class="effectiveDraftStatus(draft)"
            >
              <view class="draft-head">
                <text class="draft-title">{{ draft.display_title }}</text>
                <text class="draft-status">{{ draftStatusLabel(effectiveDraftStatus(draft)) }}</text>
              </view>
              <text class="draft-confirm">{{ draft.confirm_text }}</text>
              <view class="draft-summary">
                <text v-for="line in draftSummary(draft)" :key="line">{{ line }}</text>
              </view>
              <text v-if="effectiveDraftStatus(draft) === 'executed'" class="draft-note">已添加到档案，可到档案页查看。</text>
              <text v-else-if="effectiveDraftStatus(draft) === 'cancelled'" class="draft-note muted">这条草稿已取消。</text>
              <text v-else-if="effectiveDraftStatus(draft) === 'failed'" class="draft-note failed">{{ draft.error_message || "保存失败，请稍后重试。" }}</text>
              <view v-if="effectiveDraftStatus(draft) === 'pending'" class="draft-actions">
                <button
                  class="save-button"
                  :disabled="draftBusyId === draft.id"
                  hover-class="button-tap"
                  @tap="confirmDraft(draft)"
                >
                  {{ draftBusyId === draft.id ? "保存中" : "确认保存" }}
                </button>
                <button
                  class="cancel-button"
                  :disabled="draftBusyId === draft.id"
                  hover-class="button-tap"
                  @tap="cancelDraft(draft)"
                >
                  取消
                </button>
              </view>
            </view>
          </view>

          <view v-if="sending" class="message-item assistant">
            <view class="bubble loading-bubble">
              <text>正在整理回复...</text>
            </view>
          </view>

          <view v-if="errorMessage" class="error-card">
            <text>{{ errorMessage }}</text>
            <button v-if="lastMessage || lastImages.length" hover-class="button-tap" @tap="retryLastMessage">重试</button>
          </view>
          <view id="bottom-anchor"></view>
        </view>
      </view>
    </scroll-view>

    <view class="input-panel">
      <view v-if="imageUrls.length > 0" class="selected-images">
        <view v-for="(url, index) in imageUrls" :key="url" class="selected-image-wrap">
          <image class="selected-image" :src="mediaUrl(url)" mode="aspectFill" />
          <text class="remove-image" @tap="removeImage(index)">×</text>
        </view>
      </view>
      <view class="input-row">
        <button class="image-button" :disabled="uploading" hover-class="button-tap" @tap="chooseImage">
          {{ uploading ? "…" : "＋" }}
        </button>
        <textarea
          v-model="draft"
          class="message-input"
          auto-height
          maxlength="1000"
          confirm-type="send"
          :adjust-position="true"
          placeholder="问养宠问题，或记录体重 4.8kg"
        />
        <button class="send-button" :disabled="sendDisabled" hover-class="button-tap" @tap="sendMessage">
          {{ sending ? "发送中" : "发送" }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onLoad } from "@dcloudio/uni-app";
import { computed, nextTick, ref } from "vue";

import {
  cancelActionDraft,
  confirmActionDraft,
  consultAI,
  getConversationActionDrafts,
  getConversationMessages,
} from "@/api/ai";
import { uploadFile } from "@/api/files";
import { getPets } from "@/api/pets";
import { resolveMediaUrl } from "@/api/request";
import type { AIActionDraft, AIActionDraftStatus, AIConsultationResult } from "@/types/ai";
import type { Pet } from "@/types/pet";
import { requireAuth } from "@/utils/auth";

interface LocalMessage {
  id: string;
  serverId?: number;
  role: "user" | "assistant";
  content: string;
  imageUrls: string[];
  result?: AIConsultationResult | null;
  actionDrafts: AIActionDraft[];
}

const SELECTED_PET_STORAGE_KEY = "selected_pet_id";

const pets = ref<Pet[]>([]);
const selectedPetId = ref<number | null>(null);
const conversationId = ref<number | null>(null);
const draft = ref("");
const imageUrls = ref<string[]>([]);
const localMessages = ref<LocalMessage[]>([]);
const sending = ref(false);
const uploading = ref(false);
const errorMessage = ref("");
const lastMessage = ref("");
const lastImages = ref<string[]>([]);
const scrollAnchor = ref("");
const activeQuickIndex = ref(0);
const draftBusyId = ref<number | null>(null);
const failedImageUrls = ref<string[]>([]);

const quickGroups = [
  {
    title: "健康咨询",
    items: ["呕吐怎么办", "拉稀怎么办", "不吃饭怎么办", "皮肤瘙痒怎么办"],
  },
  {
    title: "日常养护",
    items: ["今天吃多少合适？", "怎么给猫换粮？", "多久洗一次澡？", "晚上太活跃怎么办？"],
  },
  {
    title: "档案记录",
    items: ["记录豆豆今天体重 4.8kg", "记录今天做了体外驱虫", "记录今天接种了疫苗", "记录豆豆对鸡肉过敏"],
  },
];

const selectedPet = computed(() => pets.value.find((pet) => pet.id === selectedPetId.value) || null);
const activeQuickItems = computed(() => quickGroups[activeQuickIndex.value]?.items || []);
const sendDisabled = computed(
  () => sending.value || uploading.value || !selectedPetId.value || (!draft.value.trim() && imageUrls.value.length === 0),
);

onLoad(async (query) => {
  if (!requireAuth()) {
    return;
  }
  const petId = Number(query?.petId);
  const initialQuestion = typeof query?.question === "string" ? decodeURIComponent(query.question) : "";
  conversationId.value = query?.conversationId ? Number(query.conversationId) : null;
  await loadPets(petId);
  if (conversationId.value) {
    await loadHistory(conversationId.value);
  }
  if (initialQuestion) {
    draft.value = initialQuestion;
  }
});

async function loadPets(preferredPetId?: number) {
  try {
    const response = await getPets();
    pets.value = response.data;
    const savedPetId = Number(uni.getStorageSync(SELECTED_PET_STORAGE_KEY));
    const candidate = preferredPetId || savedPetId;
    selectedPetId.value = pets.value.some((pet) => pet.id === candidate)
      ? candidate
      : pets.value[0]?.id || null;
    if (selectedPetId.value) {
      uni.setStorageSync(SELECTED_PET_STORAGE_KEY, String(selectedPetId.value));
    }
  } catch (error) {
    errorMessage.value = "宠物列表加载失败，请返回后重试";
  }
}

async function loadHistory(id: number) {
  try {
    const [messageResponse, draftResponse] = await Promise.all([
      getConversationMessages(id),
      getConversationActionDrafts(id),
    ]);
    const draftsByMessage = new Map<number, AIActionDraft[]>();
    draftResponse.data.forEach((item) => {
      const sourceId = item.source_message || 0;
      const list = draftsByMessage.get(sourceId) || [];
      list.push(item);
      draftsByMessage.set(sourceId, list);
    });
    localMessages.value = messageResponse.data
      .filter((message) => message.role !== "system")
      .map((message) => ({
        id: `remote-${message.id}`,
        serverId: message.id,
        role: message.role === "assistant" ? "assistant" : "user",
        content: message.content,
        imageUrls: message.image_urls || [],
        result: message.raw_response?.parsed_result?.health_result || null,
        actionDrafts: draftsByMessage.get(message.id) || [],
      }));
    scrollToBottom();
  } catch (error) {
    errorMessage.value = "历史消息加载失败";
  }
}

function selectPet(id: number) {
  selectedPetId.value = id;
  uni.setStorageSync(SELECTED_PET_STORAGE_KEY, String(id));
}

function fillQuestion(question: string) {
  draft.value = question;
}

function goCreatePet() {
  uni.navigateTo({ url: "/pages/pets/edit" });
}

async function chooseImage() {
  if (uploading.value) {
    return;
  }
  uploading.value = true;
  try {
    const chooseResponse = await uni.chooseImage({ count: 3, sizeType: ["compressed"] });
    const paths = chooseResponse.tempFilePaths || [];
    for (const path of paths) {
      const file = await uploadFile(path, "ai");
      imageUrls.value.push(file.url);
    }
  } catch (error) {
    uni.showToast({ title: "图片上传失败", icon: "none" });
  } finally {
    uploading.value = false;
  }
}

function removeImage(index: number) {
  imageUrls.value.splice(index, 1);
}

async function sendMessage() {
  const content = draft.value.trim();
  if ((!content && imageUrls.value.length === 0) || !selectedPetId.value || sending.value) {
    return;
  }
  if (!content && imageUrls.value.length > 0) {
    uni.showToast({ title: "建议补充一句图片说明", icon: "none" });
  }
  await submitMessage(content, [...imageUrls.value]);
}

async function submitMessage(content: string, images: string[]) {
  sending.value = true;
  errorMessage.value = "";
  lastMessage.value = content;
  lastImages.value = [...images];
  draft.value = "";
  imageUrls.value = [];
  localMessages.value.push({
    id: `local-user-${Date.now()}`,
    role: "user",
    content: content || "请参考我上传的图片",
    imageUrls: images,
    actionDrafts: [],
  });
  scrollToBottom();
  try {
    const response = await consultAI({
      pet_id: selectedPetId.value as number,
      conversation_id: conversationId.value,
      message: content,
      image_urls: images,
    });
    conversationId.value = response.data.conversation_id;
    localMessages.value.push({
      id: `local-ai-${response.data.message_id}`,
      serverId: response.data.message_id,
      role: "assistant",
      content: response.data.reply,
      imageUrls: [],
      result: response.data.health_result,
      actionDrafts: response.data.action_drafts,
    });
  } catch (error) {
    errorMessage.value = "AI 养宠助手暂时不可用，请稍后重试";
  } finally {
    sending.value = false;
    scrollToBottom();
  }
}

function retryLastMessage() {
  if (lastMessage.value || lastImages.value.length) {
    submitMessage(lastMessage.value, [...lastImages.value]);
  }
}

async function confirmDraft(draft: AIActionDraft) {
  if (effectiveDraftStatus(draft) !== "pending" || draftBusyId.value) {
    return;
  }
  draftBusyId.value = draft.id;
  try {
    const response = await confirmActionDraft(draft.id);
    updateDraft(response.data);
    uni.showToast({
      title: response.data.result_ref_type === "weight_record" ? "已添加到体重记录" : "已添加到健康档案",
      icon: "none",
    });
  } catch (error) {
    uni.showToast({ title: "保存失败，请稍后重试", icon: "none" });
  } finally {
    draftBusyId.value = null;
    scrollToBottom();
  }
}

async function cancelDraft(draft: AIActionDraft) {
  if (effectiveDraftStatus(draft) !== "pending" || draftBusyId.value) {
    return;
  }
  draftBusyId.value = draft.id;
  try {
    const response = await cancelActionDraft(draft.id);
    updateDraft(response.data);
  } catch (error) {
    uni.showToast({ title: "取消失败，请稍后重试", icon: "none" });
  } finally {
    draftBusyId.value = null;
    scrollToBottom();
  }
}

function updateDraft(nextDraft: AIActionDraft) {
  localMessages.value = localMessages.value.map((message) => ({
    ...message,
    actionDrafts: message.actionDrafts.map((item) => (item.id === nextDraft.id ? nextDraft : item)),
  }));
}

function scrollToBottom() {
  nextTick(() => {
    scrollAnchor.value = "";
    setTimeout(() => {
      scrollAnchor.value = "bottom-anchor";
    }, 30);
  });
}

function goBack() {
  uni.navigateBack();
}

function petAvatarUrl(avatar: string) {
  return resolveMediaUrl(avatar) || "/static/images/default-pet-avatar.svg";
}

function mediaUrl(url: string) {
  return resolveMediaUrl(url) || url;
}

function previewImage(url: string, urls: string[]) {
  uni.previewImage({
    current: mediaUrl(url),
    urls: urls.map(mediaUrl),
  });
}

function markImageError(url: string) {
  if (!failedImageUrls.value.includes(url)) {
    failedImageUrls.value.push(url);
  }
}

function isImageFailed(url: string) {
  return failedImageUrls.value.includes(url);
}

function riskLabel(level: string) {
  return {
    low: "低风险",
    medium: "中风险",
    high: "高风险",
    unknown: "信息不足",
  }[level] || "信息不足";
}

function draftStatusLabel(status: string) {
  return {
    pending: "待确认",
    confirmed: "待确认",
    executed: "已保存",
    cancelled: "已取消",
    failed: "保存失败",
  }[status] || "待确认";
}

function effectiveDraftStatus(draft: AIActionDraft): AIActionDraftStatus {
  if (draft.status === "executed") {
    return draft.result_ref_id ? "executed" : "pending";
  }
  if (draft.status === "confirmed") {
    return "pending";
  }
  return draft.status || "pending";
}

function draftSummary(draft: AIActionDraft) {
  const payload = draft.payload || {};
  if (draft.action_type === "create_weight_record") {
    return [
      `体重：${payload.weight || "-"} kg`,
      `日期：${payload.record_date || "-"}`,
      `备注：${payload.remark || "无"}`,
    ];
  }
  return [
    `类型：${healthTypeLabel(payload.record_type)}`,
    `标题：${payload.title || "-"}`,
    `日期：${payload.record_date || "-"}`,
    `描述：${payload.description || "无"}`,
  ];
}

function healthTypeLabel(type: string) {
  return {
    vaccine: "疫苗记录",
    deworm: "驱虫记录",
    medical: "就诊记录",
    allergy: "过敏史",
    other: "其他记录",
  }[type] || "健康记录";
}
</script>

<style scoped>
.chat-page {
  height: 100vh;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background:
    radial-gradient(circle at 0% 8%, rgba(218, 239, 255, 0.9), transparent 260rpx),
    radial-gradient(circle at 100% 26%, rgba(230, 247, 255, 0.85), transparent 260rpx),
    linear-gradient(180deg, #eff8ff 0%, #fbfdff 52%, #ffffff 100%);
}

.top-bar {
  flex: 0 0 auto;
  padding: calc(14rpx + env(safe-area-inset-top)) 24rpx 10rpx;
  display: flex;
  align-items: center;
  background: rgba(239, 248, 255, 0.98);
  box-sizing: border-box;
}

.back-button,
.image-button,
.send-button,
.save-button,
.cancel-button {
  margin: 0;
  border: 0;
  padding: 0;
}

.back-button {
  width: 58rpx;
  height: 58rpx;
  border-radius: 999rpx;
  background: #ffffff;
  color: #1f8cff;
  font-size: 44rpx;
  line-height: 48rpx;
  box-shadow: 0 8rpx 22rpx rgba(30, 119, 188, 0.12);
}

.top-title {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.top-title text:first-child {
  color: #10172d;
  font-size: 30rpx;
  font-weight: 900;
  line-height: 1.18;
}

.top-title text:last-child {
  max-width: 360rpx;
  margin-top: 2rpx;
  color: #637086;
  font-size: 21rpx;
  line-height: 1.2;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.top-spacer {
  width: 58rpx;
}

.chat-tools {
  flex: 0 0 auto;
  padding: 0 22rpx 12rpx;
  background: rgba(239, 248, 255, 0.98);
  box-sizing: border-box;
  box-shadow: 0 12rpx 24rpx rgba(30, 119, 188, 0.04);
}

.disclaimer-strip {
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(235, 247, 255, 0.95);
  color: #486079;
  font-size: 21rpx;
  line-height: 1.35;
}

.pet-strip {
  margin-top: 10rpx;
}

.pet-track {
  display: inline-flex;
  gap: 12rpx;
  padding: 2rpx 2rpx 4rpx;
}

.pet-chip {
  flex: 0 0 auto;
  min-width: 128rpx;
  max-width: 178rpx;
  height: 66rpx;
  padding: 6rpx 16rpx 6rpx 8rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: rgba(255, 255, 255, 0.78);
  border: 2rpx solid transparent;
  box-sizing: border-box;
}

.pet-chip.active {
  background: #e9f5ff;
  border-color: #1f8cff;
}

.pet-chip image {
  width: 48rpx;
  height: 48rpx;
  flex: 0 0 48rpx;
  border-radius: 999rpx;
  background: #eef8ff;
}

.pet-chip text {
  min-width: 0;
  flex: 1;
  color: #637086;
  font-size: 22rpx;
  font-weight: 900;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.pet-chip.active text {
  color: #1f8cff;
}

.quick-panel {
  margin-top: 10rpx;
}

.quick-tabs,
.quick-track {
  display: inline-flex;
  gap: 12rpx;
  padding: 0 2rpx;
}

.quick-tab {
  flex: 0 0 auto;
  padding: 9rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.76);
  color: #6b778d;
  font-size: 22rpx;
  font-weight: 900;
  white-space: nowrap;
}

.quick-tab.active {
  background: #1f8cff;
  color: #ffffff;
}

.quick-chip-scroll {
  margin-top: 10rpx;
}

.quick-chip {
  flex: 0 0 auto;
  max-width: 330rpx;
  padding: 12rpx 20rpx;
  border-radius: 999rpx;
  background: #f0f8ff;
  color: #1f5fbf;
  font-size: 23rpx;
  font-weight: 900;
  white-space: nowrap;
  box-sizing: border-box;
}

.quick-chip text {
  display: block;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.message-scroll {
  flex: 1;
  min-height: 0;
}

.scroll-inner {
  padding: 8rpx 24rpx 360rpx;
  box-sizing: border-box;
}

.empty-card {
  margin-top: 34rpx;
  padding: 54rpx 32rpx;
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.empty-card image {
  width: 160rpx;
  height: 160rpx;
}

.empty-title,
.empty-text {
  display: block;
}

.empty-title {
  margin-top: 18rpx;
  color: #10172d;
  font-size: 32rpx;
  font-weight: 900;
}

.empty-text {
  margin-top: 10rpx;
  color: #7d8799;
  font-size: 25rpx;
  line-height: 1.5;
}

.empty-button {
  width: 220rpx;
  margin-top: 24rpx;
  flex: none;
}

.messages {
  padding-top: 8rpx;
}

.message-item {
  display: flex;
  flex-direction: column;
  margin-top: 18rpx;
}

.message-item.user {
  align-items: flex-end;
}

.message-item.assistant {
  align-items: flex-start;
}

.bubble {
  max-width: 84%;
  padding: 18rpx 22rpx;
  border-radius: 26rpx;
  font-size: 27rpx;
  line-height: 1.52;
  box-sizing: border-box;
  word-break: break-word;
}

.user .bubble {
  background: linear-gradient(135deg, #1f8cff, #1268ff);
  color: #fff;
  border-bottom-right-radius: 8rpx;
}

.assistant .bubble {
  background: #fff;
  color: #17213a;
  border-bottom-left-radius: 8rpx;
  box-shadow: 0 12rpx 30rpx rgba(30, 119, 188, 0.1);
}

.bubble-images {
  display: flex;
  gap: 10rpx;
  margin-top: 12rpx;
  flex-wrap: wrap;
}

.message-image-wrap,
.message-image,
.image-fallback {
  width: 188rpx;
  height: 188rpx;
  border-radius: 20rpx;
}

.message-image {
  background: #eaf4ff;
}

.image-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #edf4fb;
  color: #7d8799;
  font-size: 22rpx;
}

.loading-bubble {
  color: #7d8799;
}

.result-card,
.draft-card,
.error-card {
  width: 100%;
  margin-top: 16rpx;
  padding: 24rpx;
  border-radius: 30rpx;
  background: rgba(255, 255, 255, 0.97);
  box-shadow: 0 16rpx 42rpx rgba(30, 119, 188, 0.1);
  box-sizing: border-box;
}

.risk-row,
.draft-head,
.draft-actions {
  display: flex;
  align-items: center;
}

.risk-row,
.draft-head {
  justify-content: space-between;
  gap: 14rpx;
  margin-bottom: 16rpx;
}

.risk-pill,
.draft-status {
  padding: 9rpx 16rpx;
  border-radius: 999rpx;
  color: #fff;
  font-size: 23rpx;
  font-weight: 900;
  white-space: nowrap;
}

.risk-pill.low { background: #18b76a; }
.risk-pill.medium { background: #f59e0b; }
.risk-pill.high { background: #ef4444; }
.risk-pill.unknown { background: #8a94a6; }

.vet-flag {
  flex: 1;
  min-width: 0;
  color: #334155;
  font-size: 23rpx;
  font-weight: 900;
  text-align: right;
}

.result-section {
  margin-top: 18rpx;
}

.result-title,
.result-text,
.list-line,
.result-disclaimer text,
.draft-title,
.draft-confirm,
.draft-summary text,
.draft-note,
.error-card text {
  display: block;
}

.result-title,
.draft-title {
  color: #10172d;
  font-size: 27rpx;
  font-weight: 900;
  line-height: 1.32;
}

.draft-title {
  flex: 1;
  min-width: 0;
}

.result-text,
.list-line,
.draft-confirm,
.draft-summary text,
.draft-note {
  margin-top: 8rpx;
  color: #4b5870;
  font-size: 24rpx;
  line-height: 1.55;
  word-break: break-word;
}

.result-disclaimer {
  margin-top: 20rpx;
  padding: 16rpx;
  border-radius: 20rpx;
  background: #f0f8ff;
  color: #637086;
  font-size: 22rpx;
  line-height: 1.52;
}

.draft-card {
  border: 2rpx solid #dbeeff;
}

.draft-card.executed {
  border-color: #bcefd3;
}

.draft-card.cancelled {
  opacity: 0.76;
}

.draft-status {
  background: #1f8cff;
}

.draft-card.executed .draft-status {
  background: #18b76a;
}

.draft-card.cancelled .draft-status {
  background: #8a94a6;
}

.draft-card.failed .draft-status {
  background: #ef4444;
}

.draft-summary {
  margin-top: 14rpx;
  padding: 14rpx;
  border-radius: 20rpx;
  background: #f6fbff;
}

.draft-note {
  padding: 12rpx 16rpx;
  margin-top: 14rpx;
  border-radius: 18rpx;
  background: #edfdf4;
  color: #18a058;
  font-weight: 900;
}

.draft-note.muted {
  background: #f3f6fa;
  color: #7d8799;
}

.draft-note.failed {
  background: #fff1f2;
  color: #ef4444;
}

.draft-actions {
  gap: 14rpx;
  margin-top: 18rpx;
}

.save-button,
.cancel-button {
  flex: 1;
  height: 70rpx;
  border-radius: 999rpx;
  font-size: 25rpx;
  font-weight: 900;
  line-height: 70rpx;
}

.save-button {
  background: linear-gradient(135deg, #1f8cff, #1268ff);
  color: #fff;
}

.cancel-button {
  background: #f2f6fb;
  color: #637086;
}

.save-button[disabled],
.cancel-button[disabled] {
  opacity: 0.5;
}

.error-card {
  color: #ef4444;
  font-size: 25rpx;
}

.error-card button {
  width: 160rpx;
  height: 64rpx;
  margin: 18rpx 0 0;
  border-radius: 999rpx;
  background: #fff1f2;
  color: #ef4444;
  font-size: 24rpx;
  font-weight: 900;
}

.input-panel {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 14rpx 20rpx calc(18rpx + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 -14rpx 36rpx rgba(30, 119, 188, 0.08);
  backdrop-filter: blur(18rpx);
  box-sizing: border-box;
}

.selected-images {
  display: flex;
  gap: 12rpx;
  margin-bottom: 12rpx;
  flex-wrap: nowrap;
  overflow: hidden;
}

.selected-image-wrap {
  position: relative;
  width: 100rpx;
  height: 100rpx;
  flex: 0 0 100rpx;
}

.selected-image {
  width: 100rpx;
  height: 100rpx;
  border-radius: 18rpx;
  background: #eaf4ff;
}

.remove-image {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  width: 34rpx;
  height: 34rpx;
  border-radius: 999rpx;
  background: #17213a;
  color: #fff;
  font-size: 24rpx;
  line-height: 32rpx;
  text-align: center;
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 12rpx;
}

.image-button {
  width: 68rpx;
  height: 68rpx;
  flex: 0 0 68rpx;
  border-radius: 999rpx;
  background: #eff8ff;
  color: #1f8cff;
  font-size: 38rpx;
  line-height: 62rpx;
  font-weight: 900;
}

.message-input {
  flex: 1;
  min-width: 0;
  min-height: 68rpx;
  max-height: 156rpx;
  padding: 17rpx 20rpx;
  border-radius: 28rpx;
  background: #f6fbff;
  color: #17213a;
  font-size: 25rpx;
  line-height: 1.42;
  box-sizing: border-box;
}

.send-button {
  width: 104rpx;
  height: 68rpx;
  flex: 0 0 104rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1f8cff, #1268ff);
  color: #fff;
  font-size: 24rpx;
  font-weight: 900;
  line-height: 68rpx;
  white-space: nowrap;
  box-shadow: 0 12rpx 26rpx rgba(31, 140, 255, 0.22);
}

.image-button[disabled],
.send-button[disabled] {
  opacity: 0.48;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

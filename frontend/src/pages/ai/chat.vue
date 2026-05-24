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

    <scroll-view
      class="message-scroll"
      scroll-y
      :scroll-into-view="scrollAnchor"
      :show-scrollbar="false"
    >
      <view class="scroll-inner">
        <view class="disclaimer-strip">
          <text>健康相关建议仅供养宠护理参考，不能替代专业兽医诊断。</text>
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
          <view v-for="group in quickGroups" :key="group.title" class="quick-group">
            <text class="quick-group-title">{{ group.title }}</text>
            <scroll-view scroll-x :show-scrollbar="false">
              <view class="quick-track">
                <view
                  v-for="item in group.items"
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

        <view class="messages">
          <view v-for="item in localMessages" :key="item.id" class="message-item" :class="item.role">
            <view class="bubble">
              <text v-if="item.content">{{ item.content }}</text>
              <view v-if="item.imageUrls.length > 0" class="bubble-images">
                <image
                  v-for="url in item.imageUrls"
                  :key="url"
                  class="message-image"
                  :src="mediaUrl(url)"
                  mode="aspectFill"
                  @tap="previewImage(url, item.imageUrls)"
                />
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
              :class="draft.status"
            >
              <view class="draft-head">
                <text class="draft-title">{{ draft.display_title }}</text>
                <text class="draft-status">{{ draftStatusLabel(draft.status) }}</text>
              </view>
              <text class="draft-confirm">{{ draft.confirm_text }}</text>
              <view class="draft-summary">
                <text v-for="line in draftSummary(draft)" :key="line">{{ line }}</text>
              </view>
              <view class="draft-actions">
                <button
                  class="save-button"
                  :disabled="draft.status !== 'pending'"
                  hover-class="button-tap"
                  @tap="confirmDraft(draft)"
                >
                  确认保存
                </button>
                <button
                  class="cancel-button"
                  :disabled="draft.status !== 'pending'"
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
          placeholder="问养护问题，或说“记录今天体重 4.8kg”"
        />
        <button class="send-button" :disabled="sending || uploading" hover-class="button-tap" @tap="sendMessage">发送</button>
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
import type { AIActionDraft, AIConsultationResult } from "@/types/ai";
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
  if (draft.status !== "pending") {
    return;
  }
  try {
    const response = await confirmActionDraft(draft.id);
    updateDraft(response.data);
    uni.showToast({
      title: response.data.result_ref_type === "weight_record" ? "已添加到体重记录" : "已添加到健康档案",
      icon: "none",
    });
  } catch (error) {
    uni.showToast({ title: "保存失败，请稍后重试", icon: "none" });
  }
}

async function cancelDraft(draft: AIActionDraft) {
  if (draft.status !== "pending") {
    return;
  }
  try {
    const response = await cancelActionDraft(draft.id);
    updateDraft(response.data);
  } catch (error) {
    uni.showToast({ title: "取消失败，请稍后重试", icon: "none" });
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
    confirmed: "已确认",
    executed: "已保存",
    cancelled: "已取消",
    failed: "保存失败",
  }[status] || "待确认";
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
  min-height: 100vh;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 0% 8%, rgba(218, 239, 255, 0.9), transparent 260rpx),
    radial-gradient(circle at 100% 26%, rgba(230, 247, 255, 0.85), transparent 260rpx),
    linear-gradient(180deg, #eff8ff 0%, #fbfdff 52%, #ffffff 100%);
}

.top-bar {
  flex: 0 0 auto;
  padding: calc(24rpx + env(safe-area-inset-top)) 26rpx 18rpx;
  display: flex;
  align-items: center;
  box-sizing: border-box;
  background: rgba(239, 248, 255, 0.96);
}

.back-button,
.image-button,
.send-button,
.save-button,
.cancel-button {
  margin: 0;
  border: 0;
}

.back-button {
  width: 68rpx;
  height: 68rpx;
  border-radius: 999rpx;
  background: #ffffff;
  color: #1f8cff;
  font-size: 50rpx;
  line-height: 58rpx;
  box-shadow: 0 10rpx 24rpx rgba(30, 119, 188, 0.12);
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
  font-size: 32rpx;
  font-weight: 900;
}

.top-title text:last-child {
  max-width: 360rpx;
  margin-top: 4rpx;
  color: #637086;
  font-size: 22rpx;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.top-spacer {
  width: 68rpx;
}

.message-scroll {
  flex: 1;
  min-height: 0;
}

.scroll-inner {
  padding: 0 28rpx 250rpx;
  box-sizing: border-box;
}

.disclaimer-strip {
  margin-top: 14rpx;
  padding: 18rpx 22rpx;
  border-radius: 24rpx;
  background: rgba(235, 247, 255, 0.95);
  color: #486079;
  font-size: 23rpx;
  line-height: 1.5;
}

.pet-strip,
.quick-panel {
  margin-top: 18rpx;
  border-radius: 28rpx;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 8rpx 24rpx rgba(30, 119, 188, 0.06);
}

.pet-strip {
  padding: 18rpx 0;
}

.pet-track,
.quick-track {
  display: inline-flex;
  gap: 18rpx;
  padding: 0 18rpx;
}

.pet-chip {
  width: 126rpx;
  padding: 12rpx 10rpx;
  border-radius: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  background: #f6fbff;
  box-sizing: border-box;
}

.pet-chip.active {
  background: #e9f5ff;
  box-shadow: inset 0 0 0 3rpx #1f8cff;
}

.pet-chip image {
  width: 72rpx;
  height: 72rpx;
  border-radius: 999rpx;
}

.pet-chip text {
  width: 100%;
  color: #637086;
  font-size: 22rpx;
  font-weight: 900;
  text-align: center;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.pet-chip.active text {
  color: #1f8cff;
}

.quick-panel {
  padding: 18rpx 0 8rpx;
}

.quick-group {
  margin-bottom: 16rpx;
}

.quick-group-title {
  display: block;
  padding: 0 20rpx 10rpx;
  color: #10172d;
  font-size: 24rpx;
  font-weight: 900;
}

.quick-chip {
  flex: 0 0 auto;
  padding: 14rpx 20rpx;
  border-radius: 999rpx;
  background: #f0f8ff;
  color: #1f5fbf;
  font-size: 23rpx;
  font-weight: 900;
  white-space: nowrap;
}

.messages {
  padding-top: 20rpx;
}

.message-item {
  display: flex;
  flex-direction: column;
  margin-top: 22rpx;
}

.message-item.user {
  align-items: flex-end;
}

.message-item.assistant {
  align-items: flex-start;
}

.bubble {
  max-width: 82%;
  padding: 22rpx 26rpx;
  border-radius: 28rpx;
  font-size: 28rpx;
  line-height: 1.55;
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
  gap: 12rpx;
  margin-top: 14rpx;
  flex-wrap: wrap;
}

.message-image {
  width: 190rpx;
  height: 190rpx;
  border-radius: 20rpx;
  background: #eaf4ff;
}

.loading-bubble {
  color: #7d8799;
}

.result-card,
.draft-card,
.error-card {
  width: 100%;
  margin-top: 18rpx;
  padding: 26rpx;
  border-radius: 32rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
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
  gap: 16rpx;
  margin-bottom: 18rpx;
}

.risk-pill,
.draft-status {
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  color: #fff;
  font-size: 24rpx;
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
  font-size: 24rpx;
  font-weight: 900;
  text-align: right;
}

.result-section {
  margin-top: 20rpx;
}

.result-title,
.result-text,
.list-line,
.result-disclaimer text,
.draft-title,
.draft-confirm,
.draft-summary text,
.error-card text {
  display: block;
}

.result-title,
.draft-title {
  color: #10172d;
  font-size: 28rpx;
  font-weight: 900;
  line-height: 1.3;
}

.result-text,
.list-line,
.draft-confirm,
.draft-summary text {
  margin-top: 8rpx;
  color: #4b5870;
  font-size: 25rpx;
  line-height: 1.55;
  word-break: break-word;
}

.result-disclaimer {
  margin-top: 22rpx;
  padding: 18rpx;
  border-radius: 22rpx;
  background: #f0f8ff;
  color: #637086;
  font-size: 23rpx;
  line-height: 1.55;
}

.draft-card {
  border: 2rpx solid #e3f0ff;
}

.draft-card.executed {
  border-color: #c7f4dc;
}

.draft-card.cancelled {
  opacity: 0.72;
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
  padding: 16rpx;
  border-radius: 20rpx;
  background: #f6fbff;
}

.draft-actions {
  gap: 16rpx;
  margin-top: 18rpx;
}

.save-button,
.cancel-button {
  flex: 1;
  height: 72rpx;
  border-radius: 999rpx;
  font-size: 25rpx;
  font-weight: 900;
  line-height: 72rpx;
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
  padding: 16rpx 24rpx calc(24rpx + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 -14rpx 36rpx rgba(30, 119, 188, 0.08);
  box-sizing: border-box;
}

.selected-images {
  display: flex;
  gap: 12rpx;
  margin-bottom: 12rpx;
  flex-wrap: wrap;
}

.selected-image-wrap {
  position: relative;
  width: 108rpx;
  height: 108rpx;
}

.selected-image {
  width: 108rpx;
  height: 108rpx;
  border-radius: 18rpx;
  background: #eaf4ff;
}

.remove-image {
  position: absolute;
  top: -10rpx;
  right: -10rpx;
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
  gap: 14rpx;
}

.image-button {
  width: 72rpx;
  height: 72rpx;
  border-radius: 999rpx;
  background: #eff8ff;
  color: #1f8cff;
  font-size: 40rpx;
  line-height: 66rpx;
  font-weight: 900;
}

.message-input {
  flex: 1;
  min-height: 72rpx;
  max-height: 180rpx;
  padding: 18rpx 22rpx;
  border-radius: 28rpx;
  background: #f6fbff;
  color: #17213a;
  font-size: 26rpx;
  line-height: 1.42;
  box-sizing: border-box;
}

.send-button {
  width: 112rpx;
  height: 72rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1f8cff, #1268ff);
  color: #fff;
  font-size: 25rpx;
  font-weight: 900;
  line-height: 72rpx;
  box-shadow: 0 12rpx 26rpx rgba(31, 140, 255, 0.22);
}

.image-button[disabled],
.send-button[disabled] {
  opacity: 0.5;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

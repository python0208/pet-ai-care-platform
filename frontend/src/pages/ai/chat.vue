<template>
  <view class="chat-page">
    <view class="top-bar">
      <button class="back-button" hover-class="button-tap" @tap="goBack">‹</button>
      <view class="top-title">
        <text>AI健康咨询</text>
        <text>{{ selectedPet?.name || "宠物" }}</text>
      </view>
      <view class="top-spacer"></view>
    </view>

    <scroll-view class="message-scroll" scroll-y :scroll-into-view="scrollAnchor">
      <view class="disclaimer-strip">
        <text>本结果仅供养宠护理参考，不能替代专业兽医诊断。</text>
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

      <view class="quick-list">
        <view v-for="item in quickQuestions" :key="item" class="quick-chip" @tap="fillQuestion(item)">
          <text>{{ item }}</text>
        </view>
      </view>

      <view class="messages">
        <view v-for="item in localMessages" :key="item.id" class="message-item" :class="item.role">
          <view class="bubble">
            <text>{{ item.content }}</text>
          </view>
          <view v-if="item.result" class="result-card">
            <view class="risk-row">
              <text class="risk-pill" :class="item.result.risk_level">{{ riskLabel(item.result.risk_level) }}</text>
              <text class="vet-flag">{{ item.result.need_vet ? "建议联系线下宠物医院" : "可先观察护理" }}</text>
            </view>
            <view class="result-section">
              <text class="result-title">症状总结</text>
              <text class="result-text">{{ item.result.summary }}</text>
            </view>
            <view class="result-section">
              <text class="result-title">可能原因</text>
              <text v-for="cause in item.result.possible_causes" :key="cause" class="list-line">· {{ cause }}</text>
            </view>
            <view class="result-section">
              <text class="result-title">家庭护理建议</text>
              <text v-for="care in item.result.home_care" :key="care" class="list-line">· {{ care }}</text>
            </view>
            <view class="result-section">
              <text class="result-title">危险信号</text>
              <text v-for="sign in item.result.warning_signs" :key="sign" class="list-line">· {{ sign }}</text>
            </view>
            <view class="result-section">
              <text class="result-title">建议补充问题</text>
              <text v-for="question in item.result.questions_to_ask" :key="question" class="list-line">· {{ question }}</text>
            </view>
            <view class="result-disclaimer">
              <text>{{ item.result.disclaimer }}</text>
            </view>
          </view>
        </view>

        <view v-if="sending" class="message-item assistant">
          <view class="bubble loading-bubble">
            <text>正在整理建议...</text>
          </view>
        </view>

        <view v-if="errorMessage" class="error-card">
          <text>{{ errorMessage }}</text>
          <button v-if="lastMessage" hover-class="button-tap" @tap="retryLastMessage">重试</button>
        </view>
        <view id="bottom-anchor"></view>
      </view>
    </scroll-view>

    <view class="input-panel">
      <view v-if="imageUrls.length > 0" class="image-list">
        <view v-for="(url, index) in imageUrls" :key="url" class="image-tag">
          <text>图片 {{ index + 1 }}</text>
          <text @tap="removeImage(index)">×</text>
        </view>
      </view>
      <view class="input-row">
        <button class="image-button" hover-class="button-tap" @tap="chooseImage">＋</button>
        <textarea
          v-model="draft"
          class="message-input"
          auto-height
          maxlength="1000"
          placeholder="描述症状、持续时间、精神和食欲情况"
        />
        <button class="send-button" :disabled="sending" hover-class="button-tap" @tap="sendMessage">发送</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onLoad } from "@dcloudio/uni-app";
import { computed, nextTick, ref } from "vue";

import { consultAI, getConversationMessages } from "@/api/ai";
import { uploadFile } from "@/api/files";
import { getPets } from "@/api/pets";
import { resolveMediaUrl } from "@/api/request";
import type { AIConsultationResult } from "@/types/ai";
import type { Pet } from "@/types/pet";
import { requireAuth } from "@/utils/auth";

interface LocalMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  result?: AIConsultationResult;
}

const SELECTED_PET_STORAGE_KEY = "selected_pet_id";

const pets = ref<Pet[]>([]);
const selectedPetId = ref<number | null>(null);
const conversationId = ref<number | null>(null);
const draft = ref("");
const imageUrls = ref<string[]>([]);
const localMessages = ref<LocalMessage[]>([]);
const sending = ref(false);
const errorMessage = ref("");
const lastMessage = ref("");
const scrollAnchor = ref("");

const quickQuestions = ["呕吐怎么办", "拉稀怎么办", "不吃饭怎么办", "皮肤瘙痒怎么办"];

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
    await loadMessages(conversationId.value);
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

async function loadMessages(id: number) {
  try {
    const response = await getConversationMessages(id);
    localMessages.value = response.data
      .filter((message) => message.role !== "system")
      .map((message) => ({
        id: `remote-${message.id}`,
        role: message.role === "assistant" ? "assistant" : "user",
        content: message.content,
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
  try {
    const chooseResponse = await uni.chooseImage({ count: 3, sizeType: ["compressed"] });
    const paths = chooseResponse.tempFilePaths || [];
    for (const path of paths) {
      const file = await uploadFile(path, "ai");
      imageUrls.value.push(file.url);
    }
  } catch (error) {
    uni.showToast({ title: "图片上传失败", icon: "none" });
  }
}

function removeImage(index: number) {
  imageUrls.value.splice(index, 1);
}

async function sendMessage() {
  const content = draft.value.trim();
  if (!content || !selectedPetId.value || sending.value) {
    return;
  }
  await submitMessage(content);
}

async function submitMessage(content: string) {
  sending.value = true;
  errorMessage.value = "";
  lastMessage.value = content;
  const currentImages = [...imageUrls.value];
  draft.value = "";
  imageUrls.value = [];
  localMessages.value.push({
    id: `local-user-${Date.now()}`,
    role: "user",
    content,
  });
  scrollToBottom();
  try {
    const response = await consultAI({
      pet_id: selectedPetId.value as number,
      conversation_id: conversationId.value,
      message: content,
      image_urls: currentImages,
    });
    conversationId.value = response.data.conversation_id;
    localMessages.value.push({
      id: `local-ai-${response.data.message_id}`,
      role: "assistant",
      content: response.data.reply,
      result: response.data.result,
    });
  } catch (error) {
    errorMessage.value = "AI 服务暂时不可用，请稍后重试";
  } finally {
    sending.value = false;
    scrollToBottom();
  }
}

function retryLastMessage() {
  if (lastMessage.value) {
    submitMessage(lastMessage.value);
  }
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

function riskLabel(level: string) {
  return {
    low: "低风险",
    medium: "中风险",
    high: "高风险",
    unknown: "信息不足",
  }[level] || "信息不足";
}
</script>

<style scoped>
.chat-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 0% 8%, rgba(218, 239, 255, 0.9), transparent 260rpx),
    linear-gradient(180deg, #eff8ff 0%, #fbfdff 52%, #ffffff 100%);
}

.top-bar {
  height: 116rpx;
  padding: 34rpx 26rpx 16rpx;
  display: flex;
  align-items: center;
  box-sizing: border-box;
  background: rgba(239, 248, 255, 0.96);
}

.back-button,
.image-button,
.send-button {
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

.disclaimer-strip,
.pet-strip,
.quick-list,
.messages {
  margin: 0 28rpx;
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

.pet-strip {
  margin-top: 18rpx;
  padding: 18rpx 0;
  border-radius: 28rpx;
  background: rgba(255, 255, 255, 0.9);
}

.pet-track {
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

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
  margin-top: 18rpx;
}

.quick-chip {
  padding: 14rpx 20rpx;
  border-radius: 999rpx;
  background: #fff;
  color: #1f5fbf;
  font-size: 24rpx;
  font-weight: 900;
  box-shadow: 0 8rpx 20rpx rgba(30, 119, 188, 0.08);
}

.messages {
  padding: 20rpx 0 200rpx;
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
  max-width: 78%;
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

.loading-bubble {
  color: #7d8799;
}

.result-card,
.error-card {
  width: 100%;
  margin-top: 18rpx;
  padding: 26rpx;
  border-radius: 32rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
  box-sizing: border-box;
}

.risk-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 18rpx;
}

.risk-pill {
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  color: #fff;
  font-size: 24rpx;
  font-weight: 900;
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
.error-card text {
  display: block;
}

.result-title {
  color: #10172d;
  font-size: 28rpx;
  font-weight: 900;
  line-height: 1.3;
}

.result-text,
.list-line {
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
  padding: 16rpx 24rpx 30rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 -14rpx 36rpx rgba(30, 119, 188, 0.08);
  box-sizing: border-box;
}

.image-list {
  display: flex;
  gap: 12rpx;
  margin-bottom: 12rpx;
  flex-wrap: wrap;
}

.image-tag {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #eef8ff;
  color: #1f8cff;
  font-size: 22rpx;
  font-weight: 900;
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

.send-button[disabled] {
  opacity: 0.5;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

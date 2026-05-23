<template>
  <scroll-view class="archive-page" scroll-y>
    <view class="page-inner">
      <view class="hero-row">
        <view>
          <view class="title-row">
            <text class="page-title">档案管理</text>
            <image src="/static/icons/archive/paw_accent.png" mode="aspectFit" />
          </view>
          <text class="page-subtitle">为毛孩子建立完整健康档案</text>
        </view>
        <button class="add-button" hover-class="button-tap" @tap="goCreate">+ 新增宠物</button>
      </view>

      <view v-if="pets.length > 0" class="pet-switcher-card">
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
            <view class="pet-switch-item add-switch" @tap="goCreate">
              <view class="add-avatar">+</view>
              <text>新增</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <view v-if="loading && pets.length === 0" class="state-card">
        <image src="/static/icons/archive/add_pet.png" mode="aspectFit" />
        <text>正在整理档案...</text>
      </view>

      <view v-else-if="errorMessage" class="state-card">
        <image src="/static/icons/archive/empty_pet.png" mode="aspectFit" />
        <text>{{ errorMessage }}</text>
        <button class="primary-button" hover-class="button-tap" @tap="loadArchive">重新加载</button>
      </view>

      <view v-else-if="pets.length === 0" class="empty-card">
        <image src="/static/icons/archive/empty_pet.png" mode="aspectFit" />
        <text class="empty-title">还没有宠物档案</text>
        <text class="empty-text">为毛孩子建立第一份健康档案</text>
        <button class="primary-button" hover-class="button-tap" @tap="goCreate">新增宠物</button>
      </view>

      <template v-else-if="selectedPet">
        <view class="pet-card" :class="{ refreshing: detailLoading }" @tap="goDetail(selectedPet.id)">
          <view class="avatar-wrap">
            <image class="pet-avatar" :src="petAvatarUrl(selectedPet.avatar)" mode="aspectFill" />
            <image class="camera-badge" src="/static/icons/archive/camera_badge.png" mode="aspectFit" />
          </view>
          <view class="pet-info">
            <view class="pet-name-row">
              <text class="pet-name">{{ selectedPet.name }}</text>
              <text class="gender-symbol">{{ genderSymbol(selectedPet.gender) }}</text>
            </view>
            <text class="pet-meta">{{ selectedPet.breed || speciesLabel(selectedPet.species) }}｜{{ ageLabel(selectedPet.birthday) }}</text>
            <view class="weight-row">
              <text>体重</text>
              <text class="weight-value">{{ selectedPet.weight || "暂无" }}</text>
              <text>kg</text>
            </view>
            <view class="status-tags">
              <view class="status-tag blue">
                <image src="/static/icons/archive/neutered.png" mode="aspectFit" />
                <text>{{ selectedPet.neutered ? "已绝育" : "未绝育" }}</text>
              </view>
              <view class="status-tag green">
                <image src="/static/icons/archive/healthy_shield.png" mode="aspectFit" />
                <text>健康中</text>
              </view>
            </view>
          </view>
          <image class="card-chevron" src="/static/icons/archive/chevron_right.png" mode="aspectFit" />
        </view>

        <view class="module-panel">
          <view
            v-for="module in archiveModules"
            :key="module.title"
            class="module-card"
            :class="module.theme"
            @tap="module.action"
          >
            <image :src="module.icon" mode="aspectFit" />
            <view>
              <text class="module-title">{{ module.title }}</text>
              <text class="module-sub">{{ module.sub }}</text>
            </view>
          </view>
        </view>

        <view class="section-card">
          <view class="section-head">
            <text class="section-title">近期记录</text>
            <view class="more-link" @tap="goHealthRecords">
              <text>全部记录</text>
              <image src="/static/icons/archive/chevron_right.png" mode="aspectFit" />
            </view>
          </view>
          <view v-if="recentItems.length === 0" class="soft-empty">暂无近期记录</view>
          <view v-else class="recent-list">
            <view v-for="item in recentItems" :key="item.key" class="recent-row">
              <image :src="item.icon" mode="aspectFit" />
              <view class="recent-main">
                <view class="recent-title-row">
                  <text class="recent-title">{{ item.title }}</text>
                  <text v-if="item.status" class="status-pill" :class="item.statusTheme">{{ item.status }}</text>
                </view>
                <text class="recent-sub">{{ item.sub }}</text>
              </view>
              <image class="row-chevron" src="/static/icons/archive/chevron_right.png" mode="aspectFit" />
            </view>
          </view>
        </view>

        <view class="section-card">
          <view class="section-head">
            <view class="trend-title">
              <image src="/static/icons/archive/weight_curve.png" mode="aspectFit" />
              <text class="section-title">体重趋势</text>
            </view>
            <view class="period-chip">近30天⌄</view>
          </view>
          <view v-if="weightRecords.length === 0" class="soft-empty">暂无体重数据，添加一次记录后会生成趋势</view>
          <view v-else class="trend-chart">
            <view class="chart-grid">
              <view class="grid-line"></view>
              <view class="grid-line"></view>
              <view class="grid-line"></view>
            </view>
            <view
              v-for="(point, index) in trendPoints"
              :key="point.id"
              class="trend-point"
              :style="{ left: point.left, bottom: point.bottom }"
            >
              <view v-if="index === trendPoints.length - 1" class="point-bubble">
                <text>{{ point.weight }} kg</text>
                <text>{{ point.date }}</text>
              </view>
              <view class="dot"></view>
              <text class="date-label">{{ point.label }}</text>
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

import { getHealthRecords, getPet, getPets, getWeightRecords } from "@/api/pets";
import { resolveMediaUrl } from "@/api/request";
import type { HealthRecord, HealthRecordType, Pet, PetDetail, PetGender, PetSpecies, WeightRecord } from "@/types/pet";
import { requireAuth } from "@/utils/auth";

const SELECTED_PET_STORAGE_KEY = "selected_pet_id";

interface RecentItem {
  key: string;
  icon: string;
  title: string;
  sub: string;
  status?: string;
  statusTheme?: string;
}

const loading = ref(false);
const detailLoading = ref(false);
const errorMessage = ref("");
const pets = ref<Pet[]>([]);
const selectedPetId = ref<number | null>(null);
const selectedPet = ref<PetDetail | null>(null);
const healthRecords = ref<HealthRecord[]>([]);
const weightRecords = ref<WeightRecord[]>([]);

onShow(async () => {
  if (!requireAuth()) {
    return;
  }
  await loadArchive();
});

const vaccineCount = computed(
  () => healthRecords.value.filter((item) => item.record_type === "vaccine").length,
);
const medicalCount = computed(
  () => healthRecords.value.filter((item) => item.record_type === "medical").length,
);
const allergyCount = computed(
  () => healthRecords.value.filter((item) => item.record_type === "allergy").length,
);
const dewormText = computed(() => {
  const reminder = selectedPet.value?.reminders.find((item) => item.record_type === "deworm");
  if (!reminder) {
    return healthRecords.value.some((item) => item.record_type === "deworm") ? "内外驱正常" : "暂无记录";
  }
  return reminder.days_until <= 15 ? "即将到期" : "内外驱正常";
});

const archiveModules = computed(() => [
  {
    title: "基础信息",
    sub: "查看与编辑",
    icon: "/static/icons/archive/archive_folder.png",
    theme: "blue-module",
    action: () => selectedPet.value && goDetail(selectedPet.value.id),
  },
  {
    title: "疫苗记录",
    sub: vaccineCount.value ? `已接种 ${vaccineCount.value} 针` : "暂无记录",
    icon: "/static/icons/archive/vaccine_record.png",
    theme: "purple-module",
    action: goHealthRecords,
  },
  {
    title: "驱虫记录",
    sub: dewormText.value,
    icon: "/static/icons/archive/deworm_record.png",
    theme: "green-module",
    action: goHealthRecords,
  },
  {
    title: "就诊记录",
    sub: medicalCount.value ? `共 ${medicalCount.value} 条记录` : "暂无记录",
    icon: "/static/icons/archive/medical_record.png",
    theme: "orange-module",
    action: goHealthRecords,
  },
  {
    title: "过敏史",
    sub: allergyCount.value ? `${allergyCount.value} 条记录` : "无已知过敏",
    icon: "/static/icons/archive/allergy_shield.png",
    theme: "pink-module",
    action: goHealthRecords,
  },
  {
    title: "体重曲线",
    sub: weightRecords.value.length ? "趋势健康" : "暂无数据",
    icon: "/static/icons/archive/weight_curve.png",
    theme: "sky-module",
    action: goWeight,
  },
]);

const recentItems = computed<RecentItem[]>(() => {
  const healthItems = healthRecords.value.slice(0, 2).map((record) => ({
    key: `health-${record.id}`,
    icon: iconForRecord(record.record_type),
    title: `${typeLabel(record.record_type)}：${record.title}`,
    sub: `${record.next_remind_date ? "到期时间" : "记录时间"} ${record.next_remind_date || record.record_date}${reminderDelta(record)}`,
    status: statusForRecord(record),
    statusTheme: record.next_remind_date ? "warning" : "done",
  }));
  const latestWeight = weightRecords.value[weightRecords.value.length - 1];
  const prevWeight = weightRecords.value[weightRecords.value.length - 2];
  const weightItem = latestWeight
    ? [
        {
          key: `weight-${latestWeight.id}`,
          icon: "/static/icons/archive/weight_curve.png",
          title: `体重记录 ${latestWeight.weight} kg`,
          sub: `${weightDiff(latestWeight, prevWeight)} ${latestWeight.record_date}`,
          status: "",
          statusTheme: "",
        },
      ]
    : [];
  return [...healthItems, ...weightItem].slice(0, 3);
});

const trendPoints = computed(() => {
  const records = weightRecords.value.slice(-5);
  const values = records.map((record) => Number(record.weight));
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(max - min, 0.1);
  return records.map((record, index) => ({
    id: record.id,
    weight: record.weight,
    date: record.record_date.slice(5),
    label: record.record_date.slice(5),
    left: records.length === 1 ? "50%" : `${(index / (records.length - 1)) * 88 + 6}%`,
    bottom: `${((Number(record.weight) - min) / span) * 92 + 32}rpx`,
  }));
});

async function loadArchive() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const listResponse = await getPets();
    pets.value = listResponse.data;
    if (pets.value.length === 0) {
      selectedPetId.value = null;
      selectedPet.value = null;
      healthRecords.value = [];
      weightRecords.value = [];
      return;
    }
    const savedPetId = Number(uni.getStorageSync(SELECTED_PET_STORAGE_KEY));
    const currentIdStillExists = pets.value.some((item) => item.id === selectedPetId.value);
    const savedPetStillExists = pets.value.some((item) => item.id === savedPetId);
    const nextPetId = currentIdStillExists
      ? selectedPetId.value
      : savedPetStillExists
        ? savedPetId
        : pets.value[0].id;
    uni.setStorageSync(SELECTED_PET_STORAGE_KEY, String(nextPetId));
    await selectPet(nextPetId, false);
  } catch (error) {
    errorMessage.value = "档案加载失败，请稍后重试";
    uni.showToast({ title: "档案加载失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

async function selectPet(petId: number | null, persist = true) {
  if (!petId || (persist && petId === selectedPetId.value && selectedPet.value)) {
    return;
  }
  selectedPetId.value = petId;
  if (persist) {
    uni.setStorageSync(SELECTED_PET_STORAGE_KEY, String(petId));
  }
  detailLoading.value = true;
  errorMessage.value = "";
  try {
    const [detailResponse, healthResponse, weightResponse] = await Promise.all([
      getPet(petId),
      getHealthRecords(petId),
      getWeightRecords(petId),
    ]);
    selectedPet.value = detailResponse.data;
    healthRecords.value = healthResponse.data;
    weightRecords.value = weightResponse.data;
  } catch (error) {
    errorMessage.value = "当前宠物档案加载失败";
    uni.showToast({ title: "当前宠物加载失败", icon: "none" });
  } finally {
    detailLoading.value = false;
  }
}

function goCreate() {
  uni.navigateTo({ url: "/pages/pets/edit" });
}

function goDetail(id: number) {
  uni.navigateTo({ url: `/pages/pets/detail?id=${id}` });
}

function goHealthRecords() {
  if (selectedPet.value) {
    uni.navigateTo({ url: `/pages/pets/health-records?petId=${selectedPet.value.id}` });
  }
}

function goWeight() {
  if (selectedPet.value) {
    uni.navigateTo({ url: `/pages/pets/weight?petId=${selectedPet.value.id}` });
  }
}

function petAvatarUrl(avatar: string) {
  return resolveMediaUrl(avatar) || "/static/images/default-pet-avatar.svg";
}

function speciesLabel(value: PetSpecies) {
  return { cat: "猫", dog: "狗", other: "其他" }[value];
}

function genderSymbol(value: PetGender) {
  return { male: "♂", female: "♀", unknown: "·" }[value];
}

function ageLabel(birthday: string | null) {
  if (!birthday) {
    return "年龄待补充";
  }
  const birth = new Date(birthday);
  const now = new Date();
  const months = Math.max(0, (now.getFullYear() - birth.getFullYear()) * 12 + now.getMonth() - birth.getMonth());
  return `${Math.floor(months / 12)}岁${months % 12}个月`;
}

function typeLabel(type: HealthRecordType) {
  return { vaccine: "疫苗接种", deworm: "驱虫提醒", medical: "就诊记录", allergy: "过敏记录", other: "健康记录" }[type];
}

function iconForRecord(type: HealthRecordType) {
  return {
    vaccine: "/static/icons/archive/vaccine_record.png",
    deworm: "/static/icons/archive/deworm_record.png",
    medical: "/static/icons/archive/medical_record.png",
    allergy: "/static/icons/archive/allergy_shield.png",
    other: "/static/icons/archive/recent_clock.png",
  }[type];
}

function statusForRecord(record: HealthRecord) {
  if (!record.next_remind_date) {
    return "已完成";
  }
  return new Date(record.next_remind_date).getTime() >= Date.now() ? "即将到期" : "已过期";
}

function reminderDelta(record: HealthRecord) {
  if (!record.next_remind_date) {
    return "";
  }
  const diff = Math.ceil((new Date(record.next_remind_date).getTime() - Date.now()) / 86400000);
  return diff >= 0 ? `（还有 ${diff} 天）` : `（已过期 ${Math.abs(diff)} 天）`;
}

function weightDiff(current: WeightRecord, previous?: WeightRecord) {
  if (!previous) {
    return "首次记录";
  }
  const diff = Number(current.weight) - Number(previous.weight);
  if (diff === 0) {
    return "较上次 持平";
  }
  return `较上次 ${diff > 0 ? "+" : ""}${diff.toFixed(1)} kg`;
}
</script>

<style scoped>
.archive-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 0% 12%, rgba(218, 239, 255, 0.92), transparent 260rpx),
    radial-gradient(circle at 100% 30%, rgba(238, 248, 255, 0.92), transparent 260rpx),
    linear-gradient(180deg, #eff8ff 0%, #fbfdff 54%, #ffffff 100%);
}

.page-inner {
  min-height: 100vh;
  padding: 48rpx 30rpx 58rpx;
  box-sizing: border-box;
}

.hero-row,
.title-row,
.pet-name-row,
.weight-row,
.status-tags,
.status-tag,
.section-head,
.more-link,
.trend-title,
.recent-title-row {
  display: flex;
  align-items: center;
}

.hero-row {
  justify-content: space-between;
  gap: 24rpx;
}

.title-row {
  gap: 10rpx;
}

.title-row image {
  width: 42rpx;
  height: 42rpx;
}

.page-title {
  color: #10172d;
  font-size: 56rpx;
  font-weight: 900;
  line-height: 1.12;
}

.page-subtitle {
  display: block;
  margin-top: 10rpx;
  color: #637086;
  font-size: 28rpx;
  line-height: 1.35;
}

.add-button,
.primary-button {
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1f8cff, #1268ff);
  color: #fff;
  font-weight: 900;
  box-shadow: 0 16rpx 32rpx rgba(31, 140, 255, 0.24);
}

.add-button {
  width: 190rpx;
  height: 82rpx;
  margin: 0;
  flex: 0 0 190rpx;
  font-size: 26rpx;
  line-height: 82rpx;
  white-space: nowrap;
}

.state-card,
.empty-card,
.pet-switcher-card,
.pet-card,
.module-panel,
.section-card {
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
}

.pet-switcher-card {
  margin-top: 30rpx;
  padding: 22rpx 0 18rpx;
  overflow: hidden;
}

.pet-switcher {
  width: 100%;
  white-space: nowrap;
}

.pet-switch-track {
  display: inline-flex;
  align-items: flex-start;
  gap: 20rpx;
  padding: 0 22rpx;
  min-width: 100%;
  box-sizing: border-box;
}

.pet-switch-item {
  width: 112rpx;
  flex: 0 0 112rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.pet-switch-item image,
.add-avatar {
  width: 88rpx;
  height: 88rpx;
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
  line-height: 1.2;
  text-align: center;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.pet-switch-item.active text {
  color: #1f8cff;
}

.add-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx dashed #9ccfff;
  color: #1f8cff;
  font-size: 46rpx;
  font-weight: 900;
}

.state-card,
.empty-card {
  margin-top: 34rpx;
  padding: 54rpx 34rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.state-card image,
.empty-card image {
  width: 170rpx;
  height: 170rpx;
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

.primary-button {
  width: 240rpx;
  height: 82rpx;
  margin-top: 28rpx;
  font-size: 28rpx;
}

.pet-card {
  position: relative;
  min-height: 210rpx;
  margin-top: 28rpx;
  padding: 28rpx;
  display: flex;
  align-items: center;
  gap: 28rpx;
  box-sizing: border-box;
  overflow: hidden;
  transition: opacity 0.18s ease;
}

.pet-card.refreshing {
  opacity: 0.68;
}

.avatar-wrap {
  position: relative;
  width: 150rpx;
  height: 150rpx;
  flex: 0 0 150rpx;
}

.pet-avatar {
  width: 150rpx;
  height: 150rpx;
  border-radius: 999rpx;
  background: #eaf6ff;
}

.camera-badge {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 46rpx;
  height: 46rpx;
  border-radius: 999rpx;
  box-shadow: 0 8rpx 18rpx rgba(31, 140, 255, 0.18);
}

.pet-info {
  flex: 1;
  min-width: 0;
}

.pet-name-row {
  gap: 12rpx;
  min-width: 0;
}

.pet-name {
  flex: 1;
  min-width: 0;
  color: #10172d;
  font-size: 48rpx;
  font-weight: 900;
  line-height: 1.16;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.gender-symbol {
  color: #1f8cff;
  font-size: 32rpx;
  font-weight: 900;
}

.pet-meta {
  display: block;
  margin-top: 10rpx;
  color: #263049;
  font-size: 27rpx;
  line-height: 1.35;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.weight-row {
  gap: 10rpx;
  margin-top: 14rpx;
  color: #1d2740;
  font-size: 26rpx;
}

.weight-value {
  color: #1f8cff;
  font-size: 36rpx;
  font-weight: 900;
}

.status-tags {
  gap: 14rpx;
  margin-top: 18rpx;
  flex-wrap: wrap;
}

.status-tag {
  gap: 8rpx;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  font-weight: 900;
  white-space: nowrap;
}

.status-tag image {
  width: 30rpx;
  height: 30rpx;
}

.status-tag.blue {
  background: #edf7ff;
  color: #1f8cff;
}

.status-tag.green {
  background: #eafaf1;
  color: #18b76a;
}

.card-chevron {
  width: 30rpx;
  height: 30rpx;
  flex: 0 0 30rpx;
}

.module-panel {
  margin-top: 28rpx;
  padding: 22rpx;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18rpx;
}

.module-card {
  min-height: 168rpx;
  padding: 18rpx 14rpx;
  border-radius: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 10rpx;
  box-sizing: border-box;
  overflow: hidden;
}

.module-card image {
  width: 54rpx;
  height: 54rpx;
  flex: 0 0 54rpx;
}

.module-title,
.module-sub {
  display: block;
}

.module-title {
  color: #10172d;
  font-size: 28rpx;
  font-weight: 900;
  line-height: 1.2;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.module-sub {
  margin-top: 8rpx;
  color: #637086;
  font-size: 23rpx;
  line-height: 1.25;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.blue-module { background: #eff8ff; }
.purple-module { background: #f4f0ff; }
.green-module { background: #effbf4; }
.orange-module { background: #fff7eb; }
.pink-module { background: #fff2f4; }
.sky-module { background: #f0f8ff; }

.section-card {
  margin-top: 28rpx;
  padding: 26rpx;
}

.section-head {
  justify-content: space-between;
  margin-bottom: 20rpx;
  gap: 18rpx;
}

.section-title {
  color: #10172d;
  font-size: 34rpx;
  font-weight: 900;
  line-height: 1.2;
  white-space: nowrap;
}

.more-link {
  gap: 6rpx;
  flex: 0 0 auto;
  color: #7d8799;
  font-size: 24rpx;
  white-space: nowrap;
}

.more-link image {
  width: 22rpx;
  height: 22rpx;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.recent-row {
  min-height: 102rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
  padding: 18rpx;
  border: 1rpx solid #edf2f7;
  border-radius: 24rpx;
  background: #fff;
  box-sizing: border-box;
}

.recent-row > image:first-child {
  width: 58rpx;
  height: 58rpx;
  flex: 0 0 58rpx;
}

.recent-main {
  flex: 1;
  min-width: 0;
}

.recent-title-row {
  gap: 12rpx;
  min-width: 0;
  justify-content: space-between;
}

.recent-title,
.recent-sub {
  display: block;
}

.recent-title {
  flex: 1;
  min-width: 0;
  color: #10172d;
  font-size: 28rpx;
  font-weight: 900;
  line-height: 1.25;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.recent-sub {
  margin-top: 8rpx;
  color: #637086;
  font-size: 24rpx;
  line-height: 1.35;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.status-pill {
  flex: 0 0 auto;
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  font-size: 21rpx;
  font-weight: 900;
  white-space: nowrap;
}

.status-pill.done {
  background: #eafaf1;
  color: #19b96d;
}

.status-pill.warning {
  background: #fff6e5;
  color: #f59e0b;
}

.row-chevron {
  width: 26rpx;
  height: 26rpx;
  flex: 0 0 26rpx;
}

.trend-title {
  gap: 10rpx;
}

.trend-title image {
  width: 34rpx;
  height: 34rpx;
}

.period-chip {
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: #f5f8fc;
  color: #17213a;
  font-size: 24rpx;
  font-weight: 800;
}

.trend-chart {
  position: relative;
  height: 250rpx;
  overflow: hidden;
  border-radius: 22rpx;
  background: linear-gradient(180deg, rgba(232, 244, 255, 0.72), rgba(255, 255, 255, 0.2));
}

.chart-grid {
  position: absolute;
  inset: 28rpx 18rpx 48rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.grid-line {
  height: 1rpx;
  border-top: 1rpx dashed #dce7f4;
}

.trend-point {
  position: absolute;
  transform: translateX(-50%);
}

.dot {
  width: 18rpx;
  height: 18rpx;
  border: 6rpx solid #fff;
  border-radius: 999rpx;
  background: #1f8cff;
  box-shadow: 0 4rpx 12rpx rgba(31, 140, 255, 0.26);
}

.point-bubble {
  position: absolute;
  left: 18rpx;
  bottom: 18rpx;
  min-width: 104rpx;
  padding: 10rpx 14rpx;
  border-radius: 18rpx;
  background: #1f8cff;
  color: #fff;
  font-size: 22rpx;
  font-weight: 900;
}

.point-bubble text {
  display: block;
}

.date-label {
  position: absolute;
  top: 24rpx;
  left: 50%;
  transform: translateX(-50%);
  color: #637086;
  font-size: 22rpx;
  white-space: nowrap;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

<template>
  <scroll-view class="records-page" scroll-y>
    <view class="page-inner">
      <view class="top-row">
        <view>
          <text class="page-title">健康记录</text>
          <text class="page-subtitle">疫苗、驱虫、就诊和过敏都在这里</text>
        </view>
        <button class="add-button" hover-class="button-tap" @tap="goCreate">新增</button>
      </view>

      <view v-if="records.length === 0" class="empty-card">
        <image src="/static/icons/png/vaccine_record.png" mode="aspectFit" />
        <text class="empty-title">暂无健康记录</text>
        <text class="empty-text">添加疫苗或驱虫记录后，首页会自动显示提醒。</text>
      </view>

      <view v-else class="record-list">
        <view v-for="record in records" :key="record.id" class="record-card" @tap="goEdit(record.id)">
          <view class="type-chip" :class="record.record_type">{{ typeLabel(record.record_type) }}</view>
          <view class="record-main">
            <text class="record-title">{{ record.title }}</text>
            <text class="record-meta">{{ record.record_date }} · {{ record.hospital || "未填写医院" }}</text>
            <text class="record-remind">{{ record.next_remind_date ? `下次提醒 ${record.next_remind_date}` : "暂无下次提醒" }}</text>
          </view>
          <image src="/static/icons/png/chevron_right.png" mode="aspectFit" />
        </view>
      </view>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { onLoad, onShow } from "@dcloudio/uni-app";
import { ref } from "vue";

import { getHealthRecords } from "@/api/pets";
import type { HealthRecord, HealthRecordType } from "@/types/pet";
import { requireAuth } from "@/utils/auth";

const petId = ref("");
const records = ref<HealthRecord[]>([]);

onLoad((query) => {
  petId.value = String(query?.petId || "");
});

onShow(async () => {
  if (!requireAuth() || !petId.value) {
    return;
  }
  const response = await getHealthRecords(petId.value);
  records.value = response.data;
});

function goCreate() {
  uni.navigateTo({ url: `/pages/pets/health-record-edit?petId=${petId.value}` });
}

function goEdit(id: number) {
  uni.navigateTo({ url: `/pages/pets/health-record-edit?petId=${petId.value}&id=${id}` });
}

function typeLabel(type: HealthRecordType) {
  return {
    vaccine: "疫苗",
    deworm: "驱虫",
    medical: "就诊",
    allergy: "过敏",
    other: "其他",
  }[type];
}
</script>

<style scoped>
.records-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef8ff 0%, #fbfdff 100%);
}

.page-inner {
  padding: 42rpx 30rpx 58rpx;
}

.top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title,
.page-subtitle {
  display: block;
}

.page-title {
  color: #10172d;
  font-size: 40rpx;
  font-weight: 900;
}

.page-subtitle {
  margin-top: 8rpx;
  color: #7d8799;
  font-size: 25rpx;
}

.add-button {
  width: 136rpx;
  height: 76rpx;
  border-radius: 999rpx;
  background: #1f8cff;
  color: #fff;
  font-size: 28rpx;
  font-weight: 900;
}

.empty-card,
.record-card {
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
}

.empty-card {
  margin-top: 30rpx;
  padding: 54rpx 34rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.empty-card image {
  width: 128rpx;
  height: 128rpx;
}

.empty-title {
  margin-top: 18rpx;
  color: #10172d;
  font-size: 32rpx;
  font-weight: 900;
}

.empty-text {
  margin-top: 12rpx;
  color: #7d8799;
  font-size: 26rpx;
}

.record-list {
  margin-top: 28rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.record-card {
  min-height: 142rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
}

.type-chip {
  width: 86rpx;
  height: 86rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24rpx;
  font-weight: 900;
}

.vaccine { background: #8b5cf6; }
.deworm { background: #10b981; }
.medical { background: #1f8cff; }
.allergy { background: #f59e0b; }
.other { background: #94a3b8; }

.record-main {
  flex: 1;
  min-width: 0;
}

.record-title,
.record-meta,
.record-remind {
  display: block;
}

.record-title {
  color: #10172d;
  font-size: 30rpx;
  font-weight: 900;
}

.record-meta,
.record-remind {
  margin-top: 8rpx;
  color: #7d8799;
  font-size: 24rpx;
}

.record-card image {
  width: 26rpx;
  height: 26rpx;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

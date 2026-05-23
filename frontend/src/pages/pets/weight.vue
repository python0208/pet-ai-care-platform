<template>
  <scroll-view class="weight-page" scroll-y>
    <view class="page-inner">
      <text class="page-title">体重记录</text>
      <view class="form-card">
        <label class="field"><text>体重 kg</text><input v-model="form.weight" type="digit" placeholder="例如：4.8" /></label>
        <label class="field"><text>记录日期</text><input v-model="form.record_date" placeholder="YYYY-MM-DD" /></label>
        <label class="field"><text>备注</text><input v-model="form.remark" placeholder="可为空" /></label>
        <button class="save-button" hover-class="button-tap" @tap="submit">添加体重</button>
      </view>

      <view class="chart-card">
        <text class="section-title">体重曲线</text>
        <view v-if="records.length === 0" class="empty-line">暂无体重数据</view>
        <view v-else class="bar-chart">
          <view v-for="record in records" :key="record.id" class="bar-item">
            <view class="bar" :style="{ height: barHeight(record.weight) }"></view>
            <text>{{ record.weight }}</text>
          </view>
        </view>
      </view>

      <view class="record-list">
        <view v-for="record in records" :key="record.id" class="record-row">
          <view>
            <text class="record-weight">{{ record.weight }} kg</text>
            <text class="record-date">{{ record.record_date }} {{ record.remark || "" }}</text>
          </view>
          <button hover-class="button-tap" @tap="remove(record.id)">删除</button>
        </view>
      </view>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { onLoad, onShow } from "@dcloudio/uni-app";
import { reactive, ref } from "vue";

import { createWeightRecord, deleteWeightRecord, getWeightRecords } from "@/api/pets";
import type { WeightRecord } from "@/types/pet";
import { requireAuth } from "@/utils/auth";

const petId = ref("");
const records = ref<WeightRecord[]>([]);
const form = reactive({
  weight: "",
  record_date: new Date().toISOString().slice(0, 10),
  remark: "",
});

onLoad((query) => {
  petId.value = String(query?.petId || "");
});

onShow(async () => {
  if (!requireAuth() || !petId.value) {
    return;
  }
  await loadRecords();
});

async function loadRecords() {
  const response = await getWeightRecords(petId.value);
  records.value = response.data;
}

async function submit() {
  if (!form.weight || !form.record_date) {
    uni.showToast({ title: "请填写体重和日期", icon: "none" });
    return;
  }
  await createWeightRecord(petId.value, { ...form });
  form.weight = "";
  form.remark = "";
  await loadRecords();
}

async function remove(id: number) {
  await deleteWeightRecord(id);
  await loadRecords();
}

function barHeight(weight: string) {
  const value = Number(weight);
  const max = Math.max(...records.value.map((item) => Number(item.weight)), 1);
  return `${Math.max(24, (value / max) * 150)}rpx`;
}
</script>

<style scoped>
.weight-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef8ff 0%, #fbfdff 100%);
}

.page-inner {
  padding: 42rpx 30rpx 58rpx;
}

.page-title,
.section-title,
.record-weight,
.record-date {
  display: block;
}

.page-title {
  color: #10172d;
  font-size: 40rpx;
  font-weight: 900;
  margin-bottom: 24rpx;
}

.form-card,
.chart-card,
.record-row {
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
}

.form-card,
.chart-card {
  padding: 26rpx;
}

.chart-card {
  margin-top: 22rpx;
}

.field {
  display: block;
  margin-bottom: 20rpx;
}

.field text {
  display: block;
  margin-bottom: 10rpx;
  color: #17213a;
  font-size: 26rpx;
  font-weight: 800;
}

.field input {
  min-height: 82rpx;
  box-sizing: border-box;
  width: 100%;
  padding: 22rpx 24rpx;
  border-radius: 24rpx;
  background: #f4f9ff;
  color: #10172d;
  font-size: 27rpx;
}

.save-button {
  height: 86rpx;
  border-radius: 999rpx;
  background: #1f8cff;
  color: #fff;
  font-size: 29rpx;
  font-weight: 900;
}

.section-title {
  margin-bottom: 18rpx;
  color: #10172d;
  font-size: 32rpx;
  font-weight: 900;
}

.empty-line {
  color: #7d8799;
  font-size: 26rpx;
}

.bar-chart {
  height: 200rpx;
  display: flex;
  align-items: flex-end;
  gap: 18rpx;
  padding-top: 22rpx;
}

.bar-item {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  color: #637086;
  font-size: 22rpx;
}

.bar {
  width: 32rpx;
  border-radius: 999rpx;
  background: linear-gradient(180deg, #6fc3ff, #1f8cff);
}

.record-list {
  margin-top: 22rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.record-row {
  padding: 22rpx 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.record-weight {
  color: #10172d;
  font-size: 30rpx;
  font-weight: 900;
}

.record-date {
  margin-top: 8rpx;
  color: #7d8799;
  font-size: 24rpx;
}

.record-row button {
  width: 116rpx;
  height: 64rpx;
  border-radius: 999rpx;
  background: #fff1ec;
  color: #f05a28;
  font-size: 24rpx;
  font-weight: 900;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

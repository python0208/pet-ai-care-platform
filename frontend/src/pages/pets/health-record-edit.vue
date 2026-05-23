<template>
  <scroll-view class="form-page" scroll-y>
    <view class="page-inner">
      <text class="title">{{ recordId ? "编辑健康记录" : "新增健康记录" }}</text>
      <view class="form-card">
        <view class="field">
          <text>记录类型</text>
          <picker :value="typeIndex" :range="typeOptions" range-key="label" @change="onTypeChange">
            <view class="picker-value">{{ typeOptions[typeIndex].label }}</view>
          </picker>
        </view>
        <label class="field"><text>标题</text><input v-model="form.title" placeholder="例如：猫三联" /></label>
        <label class="field"><text>记录日期</text><input v-model="form.record_date" placeholder="YYYY-MM-DD" /></label>
        <label class="field"><text>下次提醒日期</text><input v-model="form.next_remind_date" placeholder="YYYY-MM-DD，可为空" /></label>
        <label class="field"><text>医院</text><input v-model="form.hospital" placeholder="可为空" /></label>
        <label class="field"><text>医生</text><input v-model="form.doctor" placeholder="可为空" /></label>
        <label class="field"><text>费用</text><input v-model="form.cost" type="digit" placeholder="可为空" /></label>
        <label class="field"><text>描述</text><textarea v-model="form.description" placeholder="补充记录细节" /></label>
      </view>
      <button class="save-button" hover-class="button-tap" @tap="submit">保存记录</button>
      <button v-if="recordId" class="delete-button" hover-class="button-tap" @tap="handleDelete">删除记录</button>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { onLoad, onShow } from "@dcloudio/uni-app";
import { computed, reactive, ref } from "vue";

import { createHealthRecord, deleteHealthRecord, getHealthRecord, updateHealthRecord } from "@/api/pets";
import type { HealthRecordType } from "@/types/pet";
import { requireAuth } from "@/utils/auth";

const petId = ref("");
const recordId = ref("");
const form = reactive({
  record_type: "vaccine" as HealthRecordType,
  title: "",
  record_date: "",
  next_remind_date: "",
  hospital: "",
  doctor: "",
  cost: "",
  description: "",
});

const typeOptions = [
  { label: "疫苗", value: "vaccine" },
  { label: "驱虫", value: "deworm" },
  { label: "就诊", value: "medical" },
  { label: "过敏", value: "allergy" },
  { label: "其他", value: "other" },
] as const;

const typeIndex = computed(() => typeOptions.findIndex((item) => item.value === form.record_type));

onLoad((query) => {
  petId.value = String(query?.petId || "");
  recordId.value = String(query?.id || "");
});

onShow(async () => {
  if (!requireAuth()) {
    return;
  }
  if (recordId.value) {
    const response = await getHealthRecord(recordId.value);
    Object.assign(form, {
      ...response.data,
      next_remind_date: response.data.next_remind_date || "",
      cost: response.data.cost || "",
    });
  }
});

function onTypeChange(event: any) {
  form.record_type = typeOptions[Number(event.detail.value)].value;
}

async function submit() {
  if (!form.title.trim() || !form.record_date.trim()) {
    uni.showToast({ title: "请填写标题和记录日期", icon: "none" });
    return;
  }
  const payload = {
    ...form,
    next_remind_date: form.next_remind_date || null,
    cost: form.cost || null,
    attachments: [],
  };
  try {
    if (recordId.value) {
      await updateHealthRecord(recordId.value, payload);
    } else {
      await createHealthRecord(petId.value, payload);
    }
    uni.showToast({ title: "已保存", icon: "success" });
    uni.navigateBack();
  } catch (error) {
    uni.showToast({ title: "保存失败", icon: "none" });
  }
}

function handleDelete() {
  uni.showModal({
    title: "删除健康记录",
    content: "删除后不可恢复。",
    success: async (result) => {
      if (!result.confirm) {
        return;
      }
      await deleteHealthRecord(recordId.value);
      uni.navigateBack();
    },
  });
}
</script>

<style scoped>
.form-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef8ff 0%, #fbfdff 100%);
}

.page-inner {
  padding: 42rpx 30rpx 58rpx;
}

.title {
  display: block;
  margin-bottom: 24rpx;
  color: #10172d;
  font-size: 40rpx;
  font-weight: 900;
}

.form-card {
  padding: 26rpx;
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
}

.field {
  display: block;
  margin-bottom: 22rpx;
}

.field text {
  display: block;
  margin-bottom: 12rpx;
  color: #17213a;
  font-size: 26rpx;
  font-weight: 800;
}

.field input,
.field textarea,
.picker-value {
  min-height: 82rpx;
  box-sizing: border-box;
  width: 100%;
  padding: 22rpx 24rpx;
  border-radius: 24rpx;
  background: #f4f9ff;
  color: #10172d;
  font-size: 27rpx;
}

.field textarea {
  height: 160rpx;
}

.save-button,
.delete-button {
  height: 90rpx;
  margin-top: 28rpx;
  border-radius: 999rpx;
  font-size: 30rpx;
  font-weight: 900;
}

.save-button {
  background: #1f8cff;
  color: #fff;
}

.delete-button {
  background: #fff1ec;
  color: #f05a28;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

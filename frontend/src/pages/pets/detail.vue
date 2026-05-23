<template>
  <scroll-view class="detail-page" scroll-y>
    <view class="page-inner" v-if="pet">
      <view class="profile-card">
        <image class="avatar" :src="pet.avatar || '/static/images/default-pet-avatar.svg'" mode="aspectFill" />
        <view class="profile-main">
          <text class="name">{{ pet.name }}</text>
          <text class="meta">{{ speciesLabel(pet.species) }} · {{ pet.breed || "未填写品种" }} · {{ ageLabel }}</text>
          <text class="weight">{{ pet.weight ? `${pet.weight} kg` : "暂无体重" }}</text>
        </view>
      </view>

      <view class="action-grid">
        <button @tap="goEdit">编辑档案</button>
        <button @tap="goHealthRecords">健康记录</button>
        <button @tap="goWeight">体重曲线</button>
      </view>

      <view class="info-card">
        <text class="section-title">最近提醒</text>
        <view v-if="pet.reminders.length === 0" class="empty-line">暂无提醒</view>
        <view v-for="item in pet.reminders" :key="item.record_type" class="reminder-row">
          <text>{{ item.record_type === "vaccine" ? "疫苗" : item.record_type === "deworm" ? "驱虫" : "健康" }}</text>
          <text>{{ item.days_until >= 0 ? `${item.days_until}天后` : `已过期${Math.abs(item.days_until)}天` }}</text>
        </view>
      </view>

      <view class="info-card">
        <text class="section-title">基础资料</text>
        <view class="info-row"><text>性别</text><text>{{ genderLabel(pet.gender) }}</text></view>
        <view class="info-row"><text>生日</text><text>{{ pet.birthday || "未填写" }}</text></view>
        <view class="info-row"><text>毛色</text><text>{{ pet.color || "未填写" }}</text></view>
        <view class="info-row"><text>绝育</text><text>{{ pet.neutered ? "已绝育" : "未绝育" }}</text></view>
        <view class="remark">{{ pet.remark || "暂无备注" }}</view>
      </view>

      <button class="delete-button" hover-class="button-tap" @tap="handleDelete">删除档案</button>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { onLoad, onShow } from "@dcloudio/uni-app";
import { computed, ref } from "vue";

import { deletePet, getPet } from "@/api/pets";
import type { PetDetail, PetGender, PetSpecies } from "@/types/pet";
import { requireAuth } from "@/utils/auth";

const petId = ref("");
const pet = ref<PetDetail | null>(null);

const ageLabel = computed(() => {
  if (!pet.value?.birthday) {
    return "年龄待补充";
  }
  const birthday = new Date(pet.value.birthday);
  const now = new Date();
  const months = Math.max(0, (now.getFullYear() - birthday.getFullYear()) * 12 + now.getMonth() - birthday.getMonth());
  return `${Math.floor(months / 12)}岁${months % 12}个月`;
});

onLoad((query) => {
  petId.value = String(query?.id || "");
});

onShow(async () => {
  if (!requireAuth()) {
    return;
  }
  if (petId.value) {
    const response = await getPet(petId.value);
    pet.value = response.data;
  }
});

function goEdit() {
  uni.navigateTo({ url: `/pages/pets/edit?id=${petId.value}` });
}

function goHealthRecords() {
  uni.navigateTo({ url: `/pages/pets/health-records?petId=${petId.value}` });
}

function goWeight() {
  uni.navigateTo({ url: `/pages/pets/weight?petId=${petId.value}` });
}

function speciesLabel(value: PetSpecies) {
  return { cat: "猫", dog: "狗", other: "其他" }[value];
}

function genderLabel(value: PetGender) {
  return { male: "公", female: "母", unknown: "未知" }[value];
}

function handleDelete() {
  uni.showModal({
    title: "删除宠物档案",
    content: "删除后健康记录和体重记录也会一起删除。",
    success: async (result) => {
      if (!result.confirm) {
        return;
      }
      await deletePet(petId.value);
      uni.showToast({ title: "已删除", icon: "success" });
      uni.switchTab({ url: "/pages/pets/index" });
    },
  });
}
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef8ff 0%, #fbfdff 100%);
}

.page-inner {
  padding: 42rpx 30rpx 58rpx;
}

.profile-card,
.info-card {
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 28rpx;
}

.avatar {
  width: 138rpx;
  height: 138rpx;
  border-radius: 999rpx;
  background: #eaf6ff;
}

.profile-main {
  flex: 1;
  min-width: 0;
}

.name,
.meta,
.weight {
  display: block;
}

.name {
  color: #10172d;
  font-size: 40rpx;
  font-weight: 900;
}

.meta {
  margin-top: 10rpx;
  color: #637086;
  font-size: 25rpx;
}

.weight {
  margin-top: 14rpx;
  color: #1f8cff;
  font-size: 34rpx;
  font-weight: 900;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
  margin: 24rpx 0;
}

.action-grid button {
  height: 84rpx;
  border-radius: 24rpx;
  background: #fff;
  color: #1f8cff;
  font-size: 26rpx;
  font-weight: 900;
  box-shadow: 0 12rpx 28rpx rgba(30, 119, 188, 0.08);
}

.info-card {
  margin-top: 22rpx;
  padding: 28rpx;
}

.section-title {
  display: block;
  margin-bottom: 18rpx;
  color: #10172d;
  font-size: 32rpx;
  font-weight: 900;
}

.reminder-row,
.info-row {
  min-height: 62rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #17213a;
  font-size: 26rpx;
}

.reminder-row text:last-child {
  color: #f59e0b;
  font-weight: 900;
}

.empty-line,
.remark {
  color: #7d8799;
  font-size: 26rpx;
  line-height: 1.55;
}

.delete-button {
  height: 88rpx;
  margin-top: 28rpx;
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

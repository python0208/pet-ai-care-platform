<template>
  <scroll-view class="pets-page" scroll-y>
    <view class="page-inner">
      <view class="top-row">
        <view>
          <text class="page-title">宠物档案</text>
          <text class="page-subtitle">每个毛孩子都有独立健康小本本</text>
        </view>
        <button class="add-button" hover-class="button-tap" @tap="goCreate">添加</button>
      </view>

      <view v-if="loading" class="state-card">
        <image src="/static/icons/png/file_paw.png" mode="aspectFit" />
        <text>正在整理档案...</text>
      </view>

      <view v-else-if="pets.length === 0" class="empty-card">
        <image src="/static/images/default-pet-avatar.svg" mode="aspectFit" />
        <text class="empty-title">还没有宠物档案</text>
        <text class="empty-text">先添加一只宠物，首页就能显示真实提醒和体重记录。</text>
        <button class="primary-button" hover-class="button-tap" @tap="goCreate">添加宠物</button>
      </view>

      <view v-else class="pet-list">
        <view v-for="pet in pets" :key="pet.id" class="pet-card" @tap="goDetail(pet.id)">
          <image
            class="pet-avatar"
            :src="pet.avatar || '/static/images/default-pet-avatar.svg'"
            mode="aspectFill"
          />
          <view class="pet-main">
            <view class="pet-head">
              <text class="pet-name">{{ pet.name }}</text>
              <text class="gender-chip">{{ genderLabel(pet.gender) }}</text>
            </view>
            <text class="pet-meta">{{ speciesLabel(pet.species) }} · {{ pet.breed || "未填写品种" }}</text>
            <view class="pet-tags">
              <text>{{ pet.weight ? `${pet.weight}kg` : "暂无体重" }}</text>
              <text>{{ pet.birthday || "生日待补充" }}</text>
            </view>
          </view>
          <image class="chevron" src="/static/icons/png/chevron_right.png" mode="aspectFit" />
        </view>
      </view>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { onShow } from "@dcloudio/uni-app";
import { ref } from "vue";

import { getPets } from "@/api/pets";
import type { Pet, PetGender, PetSpecies } from "@/types/pet";
import { requireAuth } from "@/utils/auth";

const loading = ref(false);
const pets = ref<Pet[]>([]);

onShow(async () => {
  if (!requireAuth()) {
    return;
  }
  await loadPets();
});

async function loadPets() {
  loading.value = true;
  try {
    const response = await getPets();
    pets.value = response.data;
  } catch (error) {
    uni.showToast({ title: "宠物档案加载失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function goCreate() {
  uni.navigateTo({ url: "/pages/pets/edit" });
}

function goDetail(id: number) {
  uni.navigateTo({ url: `/pages/pets/detail?id=${id}` });
}

function speciesLabel(value: PetSpecies) {
  return { cat: "猫", dog: "狗", other: "其他" }[value];
}

function genderLabel(value: PetGender) {
  return { male: "公", female: "母", unknown: "未知" }[value];
}
</script>

<style scoped>
.pets-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 92% 8%, rgba(255, 215, 160, 0.26), transparent 220rpx),
    linear-gradient(180deg, #eef8ff 0%, #fbfdff 100%);
}

.page-inner {
  min-height: 100vh;
  padding: 48rpx 30rpx 56rpx;
}

.top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
}

.page-title {
  display: block;
  color: #10172d;
  font-size: 44rpx;
  font-weight: 900;
}

.page-subtitle {
  display: block;
  margin-top: 10rpx;
  color: #7d8799;
  font-size: 25rpx;
}

.add-button,
.primary-button {
  height: 78rpx;
  border-radius: 999rpx;
  background: #1f8cff;
  color: #fff;
  font-size: 28rpx;
  font-weight: 900;
  box-shadow: 0 12rpx 28rpx rgba(31, 140, 255, 0.24);
}

.add-button {
  width: 144rpx;
  margin: 0;
}

.state-card,
.empty-card,
.pet-card {
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
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
  width: 150rpx;
  height: 150rpx;
}

.state-card text,
.empty-text {
  margin-top: 18rpx;
  color: #7d8799;
  font-size: 26rpx;
  line-height: 1.6;
}

.empty-title {
  margin-top: 22rpx;
  color: #10172d;
  font-size: 34rpx;
  font-weight: 900;
}

.primary-button {
  width: 260rpx;
  margin-top: 30rpx;
}

.pet-list {
  margin-top: 30rpx;
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}

.pet-card {
  min-height: 164rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 22rpx;
}

.pet-avatar {
  width: 116rpx;
  height: 116rpx;
  flex: 0 0 116rpx;
  border-radius: 999rpx;
  background: #eaf6ff;
}

.pet-main {
  flex: 1;
  min-width: 0;
}

.pet-head {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.pet-name {
  color: #10172d;
  font-size: 34rpx;
  font-weight: 900;
}

.gender-chip {
  padding: 5rpx 14rpx;
  border-radius: 999rpx;
  background: #edf7ff;
  color: #1f8cff;
  font-size: 22rpx;
  font-weight: 800;
}

.pet-meta {
  display: block;
  margin-top: 8rpx;
  color: #637086;
  font-size: 25rpx;
}

.pet-tags {
  margin-top: 14rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.pet-tags text {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: #fff7ec;
  color: #d97706;
  font-size: 22rpx;
  font-weight: 800;
}

.chevron {
  width: 28rpx;
  height: 28rpx;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

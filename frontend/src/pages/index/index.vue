<template>
  <scroll-view class="home-page" scroll-y>
    <view class="safe-space">
      <view class="header">
        <view>
          <view class="brand-row">
            <text class="brand-title">宠护星球</text>
            <image class="brand-icon" src="/static/icons/png/logo_star_planet.png" mode="aspectFit" />
          </view>
          <view class="greeting-row">
            <text class="greeting">你好，今天也要照顾好毛孩子</text>
            <image class="tiny-paw" src="/static/icons/png/paw.png" mode="aspectFit" />
          </view>
        </view>
        <view class="header-actions">
          <button class="icon-button" hover-class="button-tap">
            <image src="/static/icons/png/search.png" mode="aspectFit" />
          </button>
          <button class="icon-button notice-button" hover-class="button-tap">
            <image src="/static/icons/png/bell.png" mode="aspectFit" />
          </button>
        </view>
      </view>

      <view class="pet-card soft-card" @tap="handlePetCardTap">
        <view class="pet-avatar-wrap">
          <image
            class="pet-avatar"
            :src="homePetAvatarUrl"
            mode="aspectFill"
          />
          <view class="camera-dot">
            <image src="/static/icons/png/camera.png" mode="aspectFit" />
          </view>
        </view>
        <view class="pet-info">
          <view class="pet-name-row">
            <text class="pet-name">{{ homePet ? homePet.name : "还没有宠物档案" }}</text>
            <text v-if="homePet" class="gender-symbol">{{ genderSymbol }}</text>
          </view>
          <text class="pet-meta">{{ homePet ? petMeta : "添加宠物后可同步健康提醒" }}</text>
          <view v-if="homePet" class="weight-line">
            <text>体重</text>
            <text class="weight-number">{{ homeWeight }}</text>
            <text>kg</text>
          </view>
          <button v-else class="add-pet-button" hover-class="button-tap" @tap.stop="goAddPet">立即添加</button>
        </view>
        <view v-if="homePet" class="reminder-pills">
          <view class="pill pill-orange">
            <image src="/static/icons/png/deworm_bug.png" mode="aspectFit" />
            <text>驱虫</text>
            <text class="pill-strong">{{ dewormReminderText }}</text>
            <image class="chevron" src="/static/icons/png/chevron_right.png" mode="aspectFit" />
          </view>
          <view class="pill pill-green">
            <image src="/static/icons/png/vaccine_syringe.png" mode="aspectFit" />
            <text>疫苗</text>
            <text class="pill-strong">{{ vaccineReminderText }}</text>
            <image class="chevron" src="/static/icons/png/chevron_right.png" mode="aspectFit" />
          </view>
        </view>
      </view>

      <view class="ai-card">
        <view class="ai-copy">
          <view class="ai-title">
            <text class="ai-word">AI</text>
            <text>健康咨询</text>
          </view>
          <text class="ai-desc">拍照或描述症状，获取初步分析与护理建议</text>
          <button class="consult-button" hover-class="button-tap">
            <text>立即咨询</text>
            <image src="/static/icons/png/chevron_right.png" mode="aspectFit" />
          </button>
        </view>
        <view class="robot-orbit">
          <view class="heart-bubble">♥</view>
          <image class="robot-image" src="/static/icons/png/robot2.png" mode="aspectFit" />
        </view>
      </view>

      <view class="status-line" :class="healthClass">
        <text>后端连接：{{ healthLabel }}</text>
      </view>

      <view class="soft-card remind-section">
        <view class="section-head">
          <text class="section-title">今日提醒</text>
          <view class="more-link">
            <text>全部记录</text>
            <image src="/static/icons/png/chevron_right.png" mode="aspectFit" />
          </view>
        </view>
        <view class="remind-grid">
          <view
            v-for="item in reminderCards"
            :key="item.title"
            class="remind-card"
            :class="item.theme"
          >
            <image :src="item.icon" mode="aspectFit" />
            <view>
              <text class="remind-title">{{ item.title }}</text>
              <text class="remind-sub">{{ item.sub }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="quick-card soft-card">
        <view v-for="entry in quickEntries" :key="entry.title" class="quick-item" @tap="entry.action">
          <image :src="entry.icon" mode="aspectFit" />
          <text>{{ entry.title }}</text>
        </view>
      </view>

      <view class="soft-card shop-section">
        <view class="section-head">
          <view class="shop-title-row">
            <image src="/static/icons/png/shop_bag.png" mode="aspectFit" />
            <text class="section-title">精选商城</text>
          </view>
          <view class="more-link">
            <text>更多</text>
            <image src="/static/icons/png/chevron_right.png" mode="aspectFit" />
          </view>
        </view>
        <view class="product-row">
          <view v-for="product in products" :key="product.name" class="product-card">
            <view class="product-image" :class="product.theme">
              <image :src="product.icon" mode="aspectFit" />
            </view>
            <text class="product-name">{{ product.name }}</text>
            <text class="product-desc">{{ product.desc }}</text>
            <view class="price-row">
              <text class="price">¥{{ product.price }}</text>
              <button class="cart-button" hover-class="button-tap">
                <image src="/static/icons/png/cart.png" mode="aspectFit" />
              </button>
            </view>
          </view>
        </view>
      </view>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { onShow } from "@dcloudio/uni-app";
import { computed, onMounted, ref } from "vue";

import { getPet, getPets } from "@/api/pets";
import { getHealthStatus, resolveMediaUrl } from "@/api/request";
import { useAppStore } from "@/stores/app";
import type { Pet, PetDetail, PetReminder } from "@/types/pet";

const appStore = useAppStore();
const healthStatus = ref<"checking" | "ok" | "error">("checking");
const homePet = ref<Pet | null>(null);
const homePetDetail = ref<PetDetail | null>(null);

const reminderCards = computed(() => [
  {
    title: "疫苗记录",
    sub: homePetDetail.value
      ? `${homePetDetail.value.record_stats.vaccine_count}项记录`
      : "暂无数据",
    icon: "/static/icons/png/vaccine_record.png",
    theme: "purple-card",
  },
  {
    title: "驱虫记录",
    sub: homePetDetail.value?.record_stats.deworm_status || "暂无记录",
    icon: "/static/icons/png/deworm_bug.png",
    theme: "green-card",
  },
  {
    title: "体重曲线",
    sub: homePetDetail.value?.record_stats.current_weight
      ? `${homePetDetail.value.record_stats.current_weight} kg`
      : "暂无体重",
    icon: "/static/icons/png/weight_chart.png",
    theme: "blue-card",
  },
]);

const quickEntries = [
  {
    title: "宠物档案",
    icon: "/static/icons/png/pet_profile.png",
    action: () => uni.switchTab({ url: "/pages/pets/index" }),
  },
  {
    title: "AI咨询",
    icon: "/static/icons/png/ai_robot.png",
    action: () => uni.switchTab({ url: "/pages/ai/index" }),
  },
  {
    title: "附近医院",
    icon: "/static/icons/png/location_hospital.png",
    action: () => uni.switchTab({ url: "/pages/services/index" }),
  },
  {
    title: "商城",
    icon: "/static/icons/png/shop_bag.png",
    action: () => uni.showToast({ title: "商城模块后续开放", icon: "none" }),
  },
];

const products = [
  {
    name: "皇家猫粮",
    desc: "成猫全价粮 2kg",
    price: "168.00",
    icon: "/static/icons/png/paw.png",
    theme: "food-pack",
  },
  {
    name: "冻干零食",
    desc: "鸡肉冻干 80g",
    price: "39.90",
    icon: "/static/icons/png/shop_bag.png",
    theme: "snack-jar",
  },
  {
    name: "逗猫棒套装",
    desc: "羽毛+铃铛",
    price: "29.90",
    icon: "/static/icons/png/pet_profile.png",
    theme: "toy-set",
  },
];

const healthLabel = computed(() => {
  if (healthStatus.value === "ok") {
    return "正常";
  }
  if (healthStatus.value === "error") {
    return "失败";
  }
  return "检查中";
});

const healthClass = computed(() => `status-${healthStatus.value}`);
const genderSymbol = computed(() => {
  if (homePet.value?.gender === "male") {
    return "♂";
  }
  if (homePet.value?.gender === "female") {
    return "♀";
  }
  return "·";
});
const homeWeight = computed(() => homePet.value?.weight || "暂无");
const homePetAvatarUrl = computed(
  () => resolveMediaUrl(homePet.value?.avatar) || "/static/icons/png/cat_header.png",
);
const petMeta = computed(() => {
  if (!homePet.value) {
    return "";
  }
  return `${homePet.value.breed || speciesLabel(homePet.value.species)}｜${ageLabel(homePet.value.birthday)}`;
});
const dewormReminderText = computed(() => formatReminder("deworm"));
const vaccineReminderText = computed(() => formatReminder("vaccine"));

onShow(async () => {
  await loadHomePet();
});

onMounted(async () => {
  try {
    const response = await getHealthStatus();
    console.log("health check:", response);
    healthStatus.value = response.data.status === "ok" ? "ok" : "error";
  } catch (error) {
    console.log("health check failed:", error);
    healthStatus.value = "error";
  } finally {
    appStore.setBackendStatus(healthStatus.value);
  }
});

async function loadHomePet() {
  const token = uni.getStorageSync("access_token");
  if (!token) {
    homePet.value = null;
    homePetDetail.value = null;
    return;
  }
  try {
    const response = await getPets();
    homePet.value = response.data[0] || null;
    homePetDetail.value = homePet.value ? (await getPet(homePet.value.id)).data : null;
  } catch (error) {
    console.log("load pet failed:", error);
    homePet.value = null;
    homePetDetail.value = null;
  }
}

function goAddPet() {
  uni.navigateTo({ url: "/pages/pets/edit" });
}

function handlePetCardTap() {
  if (homePet.value) {
    uni.navigateTo({ url: `/pages/pets/detail?id=${homePet.value.id}` });
    return;
  }
  goAddPet();
}

function formatReminder(type: "vaccine" | "deworm") {
  const reminder = homePetDetail.value?.reminders.find(
    (item: PetReminder) => item.record_type === type,
  );
  if (!reminder) {
    return "暂无提醒";
  }
  if (reminder.days_until >= 0) {
    return `${reminder.days_until}天后`;
  }
  return `已过期${Math.abs(reminder.days_until)}天`;
}

function ageLabel(birthday: string | null) {
  if (!birthday) {
    return "年龄待补充";
  }
  const birth = new Date(birthday);
  const now = new Date();
  const months = Math.max(
    0,
    (now.getFullYear() - birth.getFullYear()) * 12 + now.getMonth() - birth.getMonth(),
  );
  return `${Math.floor(months / 12)}岁${months % 12}个月`;
}

function speciesLabel(species: string) {
  return { cat: "猫", dog: "狗", other: "其他" }[species] || "宠物";
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 98% 8%, rgba(214, 236, 255, 0.72), transparent 220rpx),
    radial-gradient(circle at 0% 22%, rgba(213, 242, 255, 0.76), transparent 260rpx),
    linear-gradient(180deg, #eef8ff 0%, #f9fcff 42%, #ffffff 100%);
}

.safe-space {
  min-height: 100vh;
  padding: 74rpx 30rpx 54rpx;
}

.header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32rpx;
}

.brand-row,
.greeting-row,
.header-actions,
.pet-name-row,
.weight-line,
.pill,
.section-head,
.more-link,
.shop-title-row,
.price-row {
  display: flex;
  align-items: center;
}

.brand-title {
  color: #10172d;
  font-size: 52rpx;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.1;
}

.brand-icon {
  width: 48rpx;
  height: 48rpx;
  margin-left: 6rpx;
}

.greeting-row {
  margin-top: 12rpx;
}

.greeting {
  color: #28324b;
  font-size: 28rpx;
  line-height: 1.4;
}

.tiny-paw {
  width: 30rpx;
  height: 30rpx;
  margin-left: 12rpx;
  opacity: 0.65;
}

.header-actions {
  gap: 20rpx;
  padding-top: 20rpx;
}

.icon-button {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-button image {
  width: 58rpx;
  height: 58rpx;
}

.notice-button {
  position: relative;
}

.notice-button::after {
  content: "";
  position: absolute;
  top: 9rpx;
  right: 7rpx;
  width: 16rpx;
  height: 16rpx;
  border: 4rpx solid #fff;
  border-radius: 999rpx;
  background: #ff5a50;
}

.soft-card {
  border: 1rpx solid rgba(255, 255, 255, 0.85);
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.11);
}

.pet-card {
  display: grid;
  grid-template-columns: 168rpx 1fr;
  column-gap: 26rpx;
  row-gap: 24rpx;
  align-items: center;
  padding: 28rpx;
}

.pet-avatar-wrap {
  position: relative;
  width: 168rpx;
  height: 168rpx;
}

.pet-avatar {
  width: 168rpx;
  height: 168rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 999rpx;
  background:
    radial-gradient(circle at 48% 34%, #fff8ef 0 32%, transparent 33%),
    linear-gradient(135deg, #ffe1b8, #fff7ef 58%, #ffd596);
  box-shadow: inset 0 0 0 8rpx rgba(255, 255, 255, 0.7);
}

.cat-face {
  color: #d88833;
  font-size: 46rpx;
  font-weight: 900;
}

.camera-dot {
  position: absolute;
  right: -4rpx;
  bottom: 4rpx;
  width: 54rpx;
  height: 54rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 5rpx solid #fff;
  border-radius: 999rpx;
  background: #f8fbff;
  box-shadow: 0 8rpx 20rpx rgba(54, 92, 137, 0.15);
}

.camera-dot image {
  width: 35rpx;
  height: 35rpx;
}

.pet-info {
  min-width: 0;
}

.pet-name {
  color: #10172d;
  font-size: 45rpx;
  font-weight: 900;
  line-height: 1.1;
}

.gender-symbol {
  margin-left: 12rpx;
  color: #247eff;
  font-size: 32rpx;
  font-weight: 800;
}

.pet-meta {
  display: block;
  margin-top: 18rpx;
  color: #263049;
  font-size: 27rpx;
  line-height: 1.35;
}

.weight-line {
  margin-top: 22rpx;
  color: #1d2740;
  font-size: 28rpx;
  gap: 10rpx;
}

.weight-number {
  color: #1c82ff;
  font-size: 42rpx;
  font-weight: 900;
}

.add-pet-button {
  width: 178rpx;
  height: 62rpx;
  margin: 20rpx 0 0;
  border-radius: 999rpx;
  background: #1f8cff;
  color: #fff;
  font-size: 24rpx;
  font-weight: 900;
  box-shadow: 0 10rpx 22rpx rgba(31, 140, 255, 0.22);
}

.reminder-pills {
  grid-column: 1 / 3;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
}

.pill {
  min-height: 76rpx;
  justify-content: center;
  gap: 8rpx;
  border-radius: 999rpx;
  color: #24304a;
  font-size: 26rpx;
  font-weight: 700;
}

.pill image {
  width: 38rpx;
  height: 38rpx;
}

.pill .chevron {
  width: 22rpx;
  height: 22rpx;
}

.pill-strong {
  font-weight: 900;
}

.pill-orange {
  background: #fff1df;
}

.pill-orange .pill-strong {
  color: #ff7727;
}

.pill-green {
  background: #eaf9ee;
}

.pill-green .pill-strong {
  color: #28bf61;
}

.ai-card {
  position: relative;
  min-height: 218rpx;
  display: flex;
  justify-content: space-between;
  margin-top: 30rpx;
  overflow: hidden;
  border-radius: 34rpx;
  background:
    radial-gradient(circle at 78% 26%, rgba(255, 255, 255, 0.9), transparent 140rpx),
    linear-gradient(135deg, #dff2ff 0%, #eff8ff 48%, #d6edff 100%);
  box-shadow: 0 20rpx 54rpx rgba(36, 136, 228, 0.16);
}

.ai-copy {
  position: relative;
  z-index: 2;
  padding: 32rpx 0 30rpx 34rpx;
}

.ai-title {
  display: flex;
  align-items: baseline;
  color: #10172d;
  font-size: 42rpx;
  font-weight: 900;
  line-height: 1.1;
}

.ai-word {
  margin-right: 10rpx;
  color: #166fff;
  font-size: 58rpx;
}

.ai-desc {
  display: block;
  max-width: 415rpx;
  margin-top: 18rpx;
  color: #33405d;
  font-size: 24rpx;
  line-height: 1.45;
}

.consult-button {
  width: 230rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  margin-top: 28rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1476ff, #1d8cff);
  box-shadow: 0 10rpx 24rpx rgba(22, 116, 255, 0.28);
  color: #fff;
  font-size: 28rpx;
  font-weight: 800;
}

.consult-button image {
  width: 24rpx;
  height: 24rpx;
  filter: brightness(0) invert(1);
}

.consult-button text {
  white-space: nowrap;
}

.robot-orbit {
  position: relative;
  width: 250rpx;
  margin-right: 28rpx;
}

.robot-image {
  position: absolute;
  right: 4rpx;
  bottom: 20rpx;
  width: 210rpx;
  height: 210rpx;
  filter: drop-shadow(0 18rpx 20rpx rgba(66, 136, 215, 0.2));
}

.heart-bubble {
  position: absolute;
  top: 42rpx;
  right: 4rpx;
  z-index: 3;
  width: 62rpx;
  height: 62rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.86);
  color: #55a7ff;
  font-size: 30rpx;
  box-shadow: 0 12rpx 26rpx rgba(48, 123, 218, 0.17);
}

.status-line {
  width: fit-content;
  margin: 18rpx 0 0 auto;
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
}

.status-checking {
  background: #edf3fb;
  color: #71809a;
}

.status-ok {
  background: #e9f8ef;
  color: #22a75b;
}

.status-error {
  background: #fff0ec;
  color: #f05a28;
}

.remind-section,
.quick-card,
.shop-section {
  margin-top: 24rpx;
  padding: 26rpx;
}

.section-head {
  justify-content: space-between;
}

.section-title {
  color: #10172d;
  font-size: 34rpx;
  font-weight: 900;
}

.more-link {
  gap: 6rpx;
  color: #737d93;
  font-size: 24rpx;
}

.more-link image {
  width: 20rpx;
  height: 20rpx;
}

.remind-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18rpx;
  margin-top: 26rpx;
}

.remind-card {
  min-width: 0;
  min-height: 124rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 14rpx;
  border-radius: 22rpx;
}

.remind-card image {
  width: 56rpx;
  height: 56rpx;
  flex: 0 0 auto;
}

.remind-title,
.remind-sub,
.product-name,
.product-desc {
  display: block;
}

.remind-title {
  color: #18213a;
  font-size: 24rpx;
  font-weight: 850;
  line-height: 1.3;
  white-space: nowrap;
}

.remind-sub {
  margin-top: 8rpx;
  color: #68748c;
  font-size: 21rpx;
  line-height: 1.25;
}

.purple-card {
  background: #f4f1ff;
}

.green-card {
  background: #effaf1;
}

.blue-card {
  background: #eff8ff;
}

.quick-card {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  padding-top: 30rpx;
  padding-bottom: 28rpx;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  color: #17213a;
  font-size: 25rpx;
  font-weight: 700;
}

.quick-item image {
  width: 82rpx;
  height: 82rpx;
}

.shop-title-row image {
  width: 38rpx;
  height: 38rpx;
  margin-right: 10rpx;
}

.product-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14rpx;
  margin-top: 22rpx;
}

.product-card {
  min-width: 0;
  padding: 14rpx;
  border: 1rpx solid #edf1f6;
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 8rpx 24rpx rgba(21, 67, 119, 0.06);
}

.product-image {
  height: 124rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18rpx;
}

.product-image image {
  width: 82rpx;
  height: 82rpx;
}

.food-pack {
  background: linear-gradient(145deg, #fff0d6, #fff8ed);
}

.snack-jar {
  background: linear-gradient(145deg, #eef7ff, #fff6ed);
}

.toy-set {
  background: linear-gradient(145deg, #fff5e6, #f2f8ff);
}

.product-name {
  margin-top: 12rpx;
  color: #18213a;
  font-size: 24rpx;
  font-weight: 850;
  line-height: 1.25;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-desc {
  margin-top: 6rpx;
  color: #7a8497;
  font-size: 20rpx;
  line-height: 1.25;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.price-row {
  justify-content: space-between;
  margin-top: 10rpx;
}

.price {
  color: #ff671f;
  font-size: 24rpx;
  font-weight: 900;
}

.cart-button {
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 999rpx;
  background: #1f82ff;
}

.cart-button image {
  width: 30rpx;
  height: 30rpx;
}

.button-tap {
  transform: scale(0.96);
  opacity: 0.86;
}
</style>

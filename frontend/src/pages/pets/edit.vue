<template>
  <scroll-view class="form-page" scroll-y>
    <view class="page-inner">
      <view class="hero">
        <view class="avatar-picker" @tap="handleAvatarUpload">
          <image :src="avatarDisplayUrl" mode="aspectFill" />
          <image class="camera-badge" src="/static/icons/archive/camera_badge.png" mode="aspectFit" />
        </view>
        <view>
          <text class="title">{{ isEdit ? "编辑宠物档案" : "新增宠物档案" }}</text>
          <text class="subtitle">资料越完整，提醒和后续咨询越贴心</text>
        </view>
      </view>

      <view class="form-card">
        <label class="field">
          <text>宠物名称</text>
          <input v-model="form.name" placeholder="例如：豆豆" />
        </label>
        <view class="field">
          <text>物种</text>
          <picker :value="speciesIndex" :range="speciesOptions" range-key="label" @change="onSpeciesChange">
            <view class="picker-value">{{ speciesOptions[speciesIndex].label }}</view>
          </picker>
        </view>
        <label class="field">
          <text>品种</text>
          <input v-model="form.breed" placeholder="例如：英短金渐层" />
        </label>
        <view class="field">
          <text>性别</text>
          <picker :value="genderIndex" :range="genderOptions" range-key="label" @change="onGenderChange">
            <view class="picker-value">{{ genderOptions[genderIndex].label }}</view>
          </picker>
        </view>
        <label class="field">
          <text>生日</text>
          <input v-model="form.birthday" placeholder="YYYY-MM-DD" />
        </label>
        <view class="avatar-tip">点击头像可从相册或相机更换宠物头像</view>
        <label class="field">
          <text>毛色</text>
          <input v-model="form.color" placeholder="例如：金色" />
        </label>
        <label class="field">
          <text>当前体重 kg</text>
          <input v-model="form.weight" type="digit" placeholder="例如：4.6" />
        </label>
        <view class="switch-row">
          <text>是否绝育</text>
          <switch :checked="form.neutered" color="#1f8cff" @change="onNeuteredChange" />
        </view>
        <label class="field">
          <text>备注</text>
          <textarea v-model="form.remark" placeholder="饮食习惯、性格、注意事项" />
        </label>
      </view>

      <button class="save-button" hover-class="button-tap" @tap="submit">{{ isEdit ? "保存修改" : "创建档案" }}</button>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { onLoad, onShow } from "@dcloudio/uni-app";
import { computed, reactive, ref } from "vue";

import { createPet, getPet, updatePet } from "@/api/pets";
import { resolveMediaUrl } from "@/api/request";
import type { PetGender, PetSpecies } from "@/types/pet";
import { choosePetAvatar, uploadPetAvatar } from "@/utils/upload";
import { requireAuth } from "@/utils/auth";

const petId = ref("");
const form = reactive({
  name: "",
  species: "cat" as PetSpecies,
  breed: "",
  gender: "unknown" as PetGender,
  birthday: "",
  avatar: "",
  color: "",
  weight: "",
  neutered: false,
  remark: "",
});

const speciesOptions = [
  { label: "猫", value: "cat" },
  { label: "狗", value: "dog" },
  { label: "其他", value: "other" },
] as const;
const genderOptions = [
  { label: "未知", value: "unknown" },
  { label: "公", value: "male" },
  { label: "母", value: "female" },
] as const;

const isEdit = computed(() => Boolean(petId.value));
const speciesIndex = computed(() => speciesOptions.findIndex((item) => item.value === form.species));
const genderIndex = computed(() => genderOptions.findIndex((item) => item.value === form.gender));
const avatarPreview = ref("");
const avatarDisplayUrl = computed(
  () => avatarPreview.value || resolveMediaUrl(form.avatar) || "/static/images/default-pet-avatar.svg",
);

onLoad((query) => {
  petId.value = String(query?.id || "");
});

onShow(async () => {
  if (!requireAuth()) {
    return;
  }
  if (petId.value) {
    await loadPet();
  }
});

async function loadPet() {
  try {
    const response = await getPet(petId.value);
    Object.assign(form, {
      name: response.data.name,
      species: response.data.species,
      breed: response.data.breed,
      gender: response.data.gender,
      birthday: response.data.birthday || "",
      avatar: response.data.avatar || "",
      color: response.data.color,
      weight: response.data.weight || "",
      neutered: response.data.neutered,
      remark: response.data.remark,
    });
  } catch (error) {
    uni.showToast({ title: "档案加载失败", icon: "none" });
  }
}

function onSpeciesChange(event: any) {
  form.species = speciesOptions[Number(event.detail.value)].value;
}

function onGenderChange(event: any) {
  form.gender = genderOptions[Number(event.detail.value)].value;
}

function onNeuteredChange(event: any) {
  form.neutered = event.detail.value;
}

async function submit() {
  if (!form.name.trim()) {
    uni.showToast({ title: "请填写宠物名称", icon: "none" });
    return;
  }
  const payload = {
    name: form.name,
    species: form.species,
    breed: form.breed,
    gender: form.gender,
    birthday: form.birthday || null,
    avatar: form.avatar,
    color: form.color,
    weight: form.weight || null,
    neutered: form.neutered,
    remark: form.remark,
  };
  try {
    const response = isEdit.value
      ? await updatePet(petId.value, payload)
      : await createPet(payload);
    uni.showToast({ title: "已保存", icon: "success" });
    uni.redirectTo({ url: `/pages/pets/detail?id=${response.data.id}` });
  } catch (error) {
    uni.showToast({ title: "保存失败，请检查表单", icon: "none" });
  }
}

async function handleAvatarUpload() {
  try {
    const filePath = await choosePetAvatar();
    avatarPreview.value = filePath;
    form.avatar = await uploadPetAvatar(filePath);
    uni.showToast({ title: "头像已上传", icon: "success" });
  } catch (error) {
    uni.showToast({ title: "头像上传失败", icon: "none" });
  }
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

.hero {
  display: flex;
  align-items: center;
  gap: 22rpx;
  margin-bottom: 26rpx;
}

.avatar-picker {
  position: relative;
  width: 116rpx;
  height: 116rpx;
  flex: 0 0 116rpx;
}

.avatar-picker > image:first-child {
  width: 116rpx;
  height: 116rpx;
  border-radius: 999rpx;
  background: #eaf6ff;
}

.camera-badge {
  position: absolute;
  right: -4rpx;
  bottom: -4rpx;
  width: 42rpx;
  height: 42rpx;
  border-radius: 999rpx;
  box-shadow: 0 8rpx 20rpx rgba(31, 140, 255, 0.2);
}

.title,
.subtitle {
  display: block;
}

.title {
  color: #10172d;
  font-size: 40rpx;
  font-weight: 900;
}

.subtitle {
  margin-top: 8rpx;
  color: #7d8799;
  font-size: 25rpx;
}

.form-card {
  padding: 26rpx;
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 18rpx 46rpx rgba(30, 119, 188, 0.1);
}

.avatar-tip {
  margin-bottom: 22rpx;
  padding: 18rpx 22rpx;
  border-radius: 22rpx;
  background: #eef8ff;
  color: #637086;
  font-size: 24rpx;
  line-height: 1.45;
}

.field {
  display: block;
  margin-bottom: 22rpx;
}

.field text,
.switch-row text {
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
  height: 150rpx;
}

.switch-row {
  min-height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.switch-row text {
  margin-bottom: 0;
}

.save-button {
  height: 92rpx;
  margin-top: 30rpx;
  border-radius: 999rpx;
  background: #1f8cff;
  color: #fff;
  font-size: 31rpx;
  font-weight: 900;
  box-shadow: 0 14rpx 34rpx rgba(31, 140, 255, 0.24);
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.9;
}
</style>

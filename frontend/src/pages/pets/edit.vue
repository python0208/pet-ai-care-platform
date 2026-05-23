<template>
  <scroll-view class="form-page" scroll-y>
    <view class="page-inner">
      <view class="hero">
        <image :src="form.avatar || '/static/images/default-pet-avatar.svg'" mode="aspectFill" />
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
        <label class="field">
          <text>头像 URL</text>
          <input v-model="form.avatar" placeholder="可为空，默认显示宠物头像" />
        </label>
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
import type { PetGender, PetSpecies } from "@/types/pet";
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
      ...response.data,
      birthday: response.data.birthday || "",
      weight: response.data.weight || "",
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
    ...form,
    birthday: form.birthday || null,
    weight: form.weight || null,
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

.hero image {
  width: 116rpx;
  height: 116rpx;
  border-radius: 999rpx;
  background: #eaf6ff;
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

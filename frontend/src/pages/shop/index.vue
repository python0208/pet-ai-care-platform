<template>
  <scroll-view
    class="shop-page"
    scroll-y
    refresher-enabled
    lower-threshold="140"
    :refresher-triggered="refreshing"
    @refresherrefresh="refreshProducts"
    @scrolltolower="loadMoreProducts"
  >
    <view class="page-body">
      <view class="hero">
        <view class="hero-copy">
          <text class="hero-title">宠物商城</text>
          <text class="hero-subtitle">严选主粮、零食与日常用品</text>
        </view>
        <image class="hero-image" src="/static/images/shop/header.png" mode="aspectFit" />
      </view>

      <view class="search-card">
        <image class="search-icon" src="/static/icons/png/search.png" mode="aspectFit" />
        <input
          class="search-input"
          placeholder="搜索商品名称 / 条码"
          confirm-type="search"
          :value="keyword"
          @input="onKeywordInput"
          @confirm="loadProducts"
        />
        <button v-if="keyword" class="clear-button" hover-class="button-tap" @tap="clearKeyword">×</button>
        <button class="scan-button" hover-class="button-tap" @tap="showScanTodo">
          <view class="scan-frame"></view>
        </button>
      </view>

      <scroll-view class="category-scroll" scroll-x :show-scrollbar="false">
        <view class="category-list">
          <button
            class="category-tab"
            :class="{ active: selectedCategoryId === '' }"
            hover-class="button-tap"
            @tap="selectCategory('')"
          >
            全部
          </button>
          <button
            v-for="category in categories"
            :key="category.id"
            class="category-tab"
            :class="{ active: selectedCategoryId === String(category.id) }"
            hover-class="button-tap"
            @tap="selectCategory(String(category.id))"
          >
            {{ category.name }}
          </button>
        </view>
      </scroll-view>
      <text v-if="categoryLoadFailed" class="category-error">分类加载失败，已为你显示全部商品</text>

      <view class="feature-banner">
        <view class="feature-copy">
          <text class="feature-title">精选好物</text>
          <text class="feature-title">让养宠更轻松</text>
          <text class="feature-pill">品质好物 · 放心之选</text>
        </view>
        <image class="feature-image" src="/static/images/shop/center.png" mode="aspectFit" />
      </view>

      <view class="section-head">
        <view class="section-title-row">
          <text class="fire-dot">●</text>
          <text class="section-title">精选推荐</text>
        </view>
        <button class="view-more" hover-class="button-tap" @tap="clearFilters">查看更多 ›</button>
      </view>

      <view v-if="loading" class="state-card">商品加载中...</view>
      <view v-else-if="loadError" class="state-card state-card-column">
        <text>商品加载失败，请稍后重试</text>
        <button class="state-action" hover-class="button-tap" @tap="loadProducts">重新加载</button>
      </view>
      <view v-else-if="products.length === 0" class="state-card">{{ emptyText }}</view>
      <view v-else class="product-grid">
        <view
          v-for="product in products"
          :key="product.id"
          class="product-card"
          hover-class="button-tap"
          @tap="goDetail(product.id)"
        >
          <view class="product-image-wrap">
            <image
              class="product-image"
              :src="productImage(product)"
              mode="aspectFit"
              @error="markImageError(product.id)"
            />
          </view>
          <view class="product-info">
            <text class="product-name">{{ product.name }}</text>
            <text class="product-spec">{{ product.spec || product.unit || "规格待补充" }}</text>
            <view class="product-bottom">
              <text class="price">¥{{ formatPrice(product.retail_price) }}</text>
              <text class="stock-tag" :class="{ empty: product.stock_status === 'out_of_stock' }">
                {{ product.stock_status === "in_stock" ? "有货" : "缺货" }}
              </text>
            </view>
          </view>
        </view>
      </view>

      <view v-if="products.length" class="load-more-state">
        <text v-if="loadingMore">加载中...</text>
        <button v-else-if="loadMoreError" class="load-more-retry" hover-class="button-tap" @tap="loadMoreProducts">
          加载失败，点击重试
        </button>
        <text v-else-if="!hasNext">没有更多商品了</text>
      </view>

      <view class="assurance-bar">
        <view v-for="item in assurances" :key="item.title" class="assurance-item">
          <text class="assurance-icon">{{ item.icon }}</text>
          <view>
            <text class="assurance-title">{{ item.title }}</text>
            <text class="assurance-sub">{{ item.sub }}</text>
          </view>
        </view>
      </view>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { onReachBottom, onShow } from "@dcloudio/uni-app";
import { computed, ref } from "vue";

import { getProductCategories, getProducts } from "@/api/shop";
import type { Product, ProductCategory } from "@/types/shop";
import { DEFAULT_PRODUCT_IMAGE, resolveProductImage } from "@/utils/productImage";

const categories = ref<ProductCategory[]>([]);
const products = ref<Product[]>([]);
const selectedCategoryId = ref("");
const keyword = ref("");
const loading = ref(false);
const loadingMore = ref(false);
const refreshing = ref(false);
const loadError = ref(false);
const loadMoreError = ref(false);
const categoryLoadFailed = ref(false);
const failedImages = ref<Set<number>>(new Set());
const page = ref(1);
const pageSize = 20;
const hasNext = ref(false);

const emptyText = computed(() => (keyword.value.trim() ? "没有找到相关商品" : "暂无商品"));

const assurances = [
  { title: "正品保障", sub: "官方严选", icon: "盾" },
  { title: "极速发货", sub: "快速送达", icon: "车" },
  { title: "安心售后", sub: "7天无忧", icon: "售" },
  { title: "会员优惠", sub: "专享折扣", icon: "惠" },
];

onShow(async () => {
  await Promise.all([loadCategories(), loadProducts()]);
});

onReachBottom(() => {
  loadMoreProducts();
});

async function loadCategories() {
  try {
    const response = await getProductCategories();
    categories.value = response.data;
    categoryLoadFailed.value = false;
  } catch (error) {
    categories.value = [];
    categoryLoadFailed.value = true;
  }
}

async function loadProducts() {
  page.value = 1;
  products.value = [];
  hasNext.value = false;
  await fetchProducts({ reset: true });
}

async function fetchProducts({ reset = false } = {}) {
  if (reset) {
    loading.value = true;
    failedImages.value = new Set();
  }
  loadError.value = false;
  loadMoreError.value = false;
  const currentPage = page.value;
  try {
    const response = await getProducts({
      q: keyword.value.trim(),
      category_id: selectedCategoryId.value || undefined,
      page: currentPage,
      page_size: pageSize,
    });
    products.value = reset ? response.data.results : [...products.value, ...response.data.results];
    hasNext.value =
      typeof response.data.has_next === "boolean"
        ? response.data.has_next
        : response.data.page * response.data.page_size < response.data.count;
    page.value = response.data.page;
  } catch (error) {
    if (reset) {
      products.value = [];
      loadError.value = true;
    } else {
      loadMoreError.value = true;
      page.value = Math.max(1, currentPage - 1);
    }
  } finally {
    if (reset) {
      loading.value = false;
      refreshing.value = false;
    }
  }
}

async function loadMoreProducts() {
  if (loading.value || loadingMore.value || !hasNext.value) {
    return;
  }
  loadingMore.value = true;
  page.value += 1;
  await fetchProducts();
  loadingMore.value = false;
}

async function refreshProducts() {
  refreshing.value = true;
  await loadProducts();
}

function onKeywordInput(event: Event) {
  keyword.value = ((event as { detail?: { value?: string } }).detail?.value || "");
}

function selectCategory(id: string) {
  selectedCategoryId.value = id;
  loadProducts();
}

function clearFilters() {
  keyword.value = "";
  selectedCategoryId.value = "";
  loadProducts();
}

function clearKeyword() {
  keyword.value = "";
  loadProducts();
}

function productImage(product: Product) {
  if (failedImages.value.has(product.id)) {
    return DEFAULT_PRODUCT_IMAGE;
  }
  return resolveProductImage(product);
}

function markImageError(id: number) {
  failedImages.value = new Set([...failedImages.value, id]);
}

function formatPrice(price: string) {
  return Number(price || 0).toFixed(2);
}

function showScanTodo() {
  uni.showToast({ title: "扫码功能开发中", icon: "none" });
}

function goDetail(id: number) {
  uni.navigateTo({ url: `/pages/shop/detail?id=${id}` });
}
</script>

<style scoped>
.shop-page {
  height: 100vh;
  overflow-y: auto;
  background:
    radial-gradient(circle at 92% 4%, rgba(181, 224, 255, 0.78), transparent 260rpx),
    radial-gradient(circle at 0% 16%, rgba(224, 244, 255, 0.92), transparent 300rpx),
    linear-gradient(180deg, #eef8ff 0%, #f8fcff 46%, #ffffff 100%);
}

.page-body {
  min-height: 100vh;
  padding: 44rpx 30rpx calc(230rpx + env(safe-area-inset-bottom));
  box-sizing: border-box;
  overflow-x: hidden;
}

.shop-page ::-webkit-scrollbar {
  display: none;
}

.hero {
  position: relative;
  min-height: 190rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hero-copy {
  position: relative;
  z-index: 2;
  max-width: 405rpx;
}

.hero-title {
  display: block;
  color: #10172d;
  font-size: 48rpx;
  font-weight: 850;
  line-height: 1.1;
}

.hero-subtitle {
  display: block;
  margin-top: 18rpx;
  color: #53627a;
  font-size: 27rpx;
  line-height: 1.35;
}

.hero-image {
  position: absolute;
  right: -42rpx;
  bottom: -18rpx;
  width: 550rpx;
  height: 270rpx;
}

.search-card {
  height: 86rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
  margin-top: 20rpx;
  padding: 0 22rpx;
  border-radius: 28rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18rpx 40rpx rgba(30, 119, 188, 0.12);
}

.search-icon {
  width: 42rpx;
  height: 42rpx;
  opacity: 0.72;
}

.search-input {
  flex: 1;
  min-width: 0;
  color: #1f2937;
  font-size: 28rpx;
}

.clear-button {
  flex: 0 0 auto;
  width: 44rpx;
  height: 44rpx;
  border-radius: 999rpx;
  background: #edf5ff;
  color: #7b8aa1;
  font-size: 34rpx;
  font-weight: 500;
  line-height: 40rpx;
}

.scan-button {
  flex: 0 0 auto;
  width: 54rpx;
  height: 54rpx;
  border-radius: 18rpx;
  background: #f3f8ff;
  line-height: 54rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scan-frame {
  width: 28rpx;
  height: 28rpx;
  border: 4rpx solid #2a8cff;
  border-radius: 6rpx;
  box-sizing: border-box;
  box-shadow: inset 0 0 0 4rpx #f3f8ff;
}

.category-scroll {
  width: 100%;
  margin-top: 28rpx;
  white-space: nowrap;
}

.category-list {
  display: inline-flex;
  align-items: center;
  gap: 42rpx;
  min-width: 100%;
  padding: 0 4rpx 12rpx;
}

.category-tab {
  position: relative;
  flex: 0 0 auto;
  max-width: 180rpx;
  height: 58rpx;
  padding: 0 2rpx;
  overflow: hidden;
  color: #20283b;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 58rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
  background: transparent;
}

.category-tab.active {
  color: #1f8cff;
  font-weight: 900;
}

.category-tab.active::after {
  content: "";
  position: absolute;
  left: 20%;
  right: 20%;
  bottom: 0;
  height: 6rpx;
  border-radius: 999rpx;
  background: #1f8cff;
}

.category-error {
  display: block;
  margin: -2rpx 4rpx 10rpx;
  color: #8b98a9;
  font-size: 23rpx;
}

.feature-banner {
  position: relative;
  min-height: 206rpx;
  display: flex;
  align-items: center;
  margin-top: 14rpx;
  overflow: hidden;
  border-radius: 28rpx;
  background:
    radial-gradient(circle at 36% 40%, rgba(255, 255, 255, 0.82), transparent 160rpx),
    linear-gradient(135deg, #dff1ff, #f1f9ff 56%, #cfe9ff);
  box-shadow: 0 14rpx 34rpx rgba(42, 132, 218, 0.12);
}

.feature-copy {
  position: relative;
  z-index: 2;
  max-width: 330rpx;
  padding-left: 38rpx;
}

.feature-title {
  display: block;
  color: #10172d;
  font-size: 34rpx;
  font-weight: 900;
  line-height: 1.22;
}

.feature-pill {
  display: inline-flex;
  margin-top: 16rpx;
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1e78ff, #5db0ff);
  color: #fff;
  font-size: 24rpx;
  font-weight: 800;
}

.feature-image {
  position: absolute;
  right: -46rpx;
  bottom: -14rpx;
  width: 530rpx;
  height: 244rpx;
}

.section-head,
.section-title-row,
.product-bottom,
.assurance-item {
  display: flex;
  align-items: center;
}

.section-head {
    display: flex;
  justify-content: space-between;
  margin: 28rpx 4rpx 18rpx;
}

.section-title-row {
  gap: 10rpx;
}

.fire-dot {
  color: #ff5a3d;
  font-size: 28rpx;
}

.section-title {
  color: #10172d;
  font-size: 32rpx;
  font-weight: 900;
}

.view-more {
  height: 50rpx;
  padding: 0 0 0 6rpx;   /* 左内边距保留，右内边距为0 */
  background: transparent;
  color: #6b768b;
  font-size: 24rpx;
  line-height: 50rpx;
  border: none;
  background: none;
  outline: none;
  text-align: right;
  margin: 0;              /* 重置外边距 */
}
.view-more::after {
  border: none;
}
.state-card {
  min-height: 160rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  border-radius: 28rpx;
  background: rgba(255, 255, 255, 0.92);
  color: #7c8798;
  font-size: 26rpx;
}

.state-card-column {
  flex-direction: column;
}

.state-action {
  height: 58rpx;
  padding: 0 28rpx;
  border-radius: 999rpx;
  background: #eaf5ff;
  color: #1f8cff;
  font-size: 25rpx;
  font-weight: 800;
  line-height: 58rpx;
}

.load-more-state {
  min-height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8b98a9;
  font-size: 24rpx;
}

.load-more-retry {
  height: 54rpx;
  padding: 0 24rpx;
  border-radius: 999rpx;
  background: #eef7ff;
  color: #1f8cff;
  font-size: 24rpx;
  font-weight: 800;
  line-height: 54rpx;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
}

.product-card {
  min-width: 0;
  overflow: hidden;
  border: 1rpx solid #e7f0fa;
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 10rpx 28rpx rgba(21, 67, 119, 0.075);
}

.product-image-wrap {
  height: 190rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 14rpx;
  border-radius: 22rpx;
  background: linear-gradient(180deg, #f0f8ff 0%, #f8fcff 100%);
}

.product-image {
  width: 100%;
  height: 168rpx;
}

.product-info {
  padding: 0 18rpx 20rpx;
}

.product-name {
  display: -webkit-box;
  min-height: 68rpx;
  overflow: hidden;
  color: #17213a;
  font-size: 26rpx;
  font-weight: 800;
  line-height: 1.32;
  text-overflow: ellipsis;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-spec {
  display: block;
  margin-top: 8rpx;
  overflow: hidden;
  color: #7f8a9e;
  font-size: 23rpx;
  line-height: 1.3;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-bottom {
  justify-content: space-between;
  gap: 12rpx;
  margin-top: 16rpx;
}

.price {
  color: #f04f32;
  font-size: 40rpx;
  font-weight: 900;
  line-height: 1;
}

.stock-tag {
  flex: 0 0 auto;
  padding: 6rpx 13rpx;
  border: 2rpx solid #28bf61;
  border-radius: 14rpx;
  background: #f0fff6;
  color: #18a45c;
  font-size: 22rpx;
  font-weight: 800;
}

.stock-tag.empty {
  border-color: #c9d3df;
  background: #f6f8fb;
  color: #8b98a9;
}

.assurance-bar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0;
  margin-top: 28rpx;
  padding: 18rpx 10rpx;
  border: 1rpx solid #e6f0fb;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 12rpx 30rpx rgba(21, 67, 119, 0.06);
}

.assurance-item {
  justify-content: center;
  gap: 8rpx;
  min-width: 0;
  border-right: 1rpx solid #edf3f9;
}

.assurance-item:last-child {
  border-right: 0;
}

.assurance-icon {
  color: #1f8cff;
  font-size: 28rpx;
  font-weight: 900;
}

.assurance-title,
.assurance-sub {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.assurance-title {
  color: #17213a;
  font-size: 22rpx;
  font-weight: 850;
}

.assurance-sub {
  margin-top: 4rpx;
  color: #7c8798;
  font-size: 19rpx;
}

.button-tap {
  transform: scale(0.97);
  opacity: 0.88;
}

button::after {
  border: 0;
}

@media (max-width: 380px) {
  .page-body {
    padding-left: 24rpx;
    padding-right: 24rpx;
  }

  .hero-title {
    font-size: 46rpx;
  }

  .hero-image {
    right: -54rpx;
    width: 380rpx;
  }

  .feature-image {
    right: -70rpx;
    width: 470rpx;
  }

  .assurance-sub {
    display: none;
  }
}
</style>

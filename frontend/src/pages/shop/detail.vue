<template>
  <view class="detail-page">
    <scroll-view class="detail-scroll" scroll-y>
      <view class="detail-body">
        <view class="image-section">
          <image class="product-image" :src="productImage" mode="aspectFit" @error="imageFailed = true" />
        </view>

        <view v-if="loading" class="empty-card">商品加载中...</view>

        <view v-if="product" class="info-card">
          <view class="price-row">
            <text class="price">¥{{ formatPrice(product.retail_price) }}</text>
            <text class="stock-tag" :class="{ empty: product.stock_status === 'out_of_stock' }">
              {{ product.stock_status === "in_stock" ? "有货" : "缺货" }}
            </text>
          </view>
          <text class="product-name">{{ product.name }}</text>
          <text class="product-spec">{{ product.spec || "规格待补充" }}</text>
        </view>

        <view v-if="product" class="detail-card">
          <view class="card-title">商品信息</view>
          <view class="detail-grid">
            <view class="detail-item">
              <text class="label">单位</text>
              <text class="value">{{ product.unit || "未填写" }}</text>
            </view>
            <view class="detail-item">
              <text class="label">重量</text>
              <text class="value">{{ product.weight ? `${product.weight}kg` : "未填写" }}</text>
            </view>
            <view class="detail-item">
              <text class="label">保质期</text>
              <text class="value">{{ product.shelf_life_months ? `${product.shelf_life_months}个月` : "未填写" }}</text>
            </view>
            <view class="detail-item">
              <text class="label">分类</text>
              <text class="value">{{ product.category?.name || "未分类" }}</text>
            </view>
            <view class="detail-item wide">
              <text class="label">条码</text>
              <text class="value">{{ product.barcode }}</text>
            </view>
            <view class="detail-item wide">
              <text class="label">当前库存</text>
              <text class="value">{{ product.total_stock }} 件</text>
            </view>
          </view>
        </view>

        <view v-if="product?.inventories?.length" class="detail-card">
          <view class="card-title">库存明细</view>
          <view v-for="inventory in product.inventories" :key="inventory.store_code" class="inventory-row">
            <text>{{ inventory.store_display_name }}</text>
            <text>{{ inventory.stock_quantity }} 件</text>
          </view>
        </view>

        <view v-if="!product && !loading" class="empty-card">{{ errorText || "商品不存在或已下架" }}</view>
      </view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="cart-button" hover-class="button-tap" @tap="showCartTodo">加入购物车</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onLoad } from "@dcloudio/uni-app";
import { computed, ref } from "vue";

import { getProductDetail } from "@/api/shop";
import type { ProductDetail } from "@/types/shop";
import { DEFAULT_PRODUCT_IMAGE, resolveProductImage } from "@/utils/productImage";

const product = ref<ProductDetail | null>(null);
const loading = ref(false);
const imageFailed = ref(false);
const errorText = ref("");

const productImage = computed(() => {
  if (imageFailed.value) {
    return DEFAULT_PRODUCT_IMAGE;
  }
  return resolveProductImage(product.value);
});

onLoad((query) => {
  const id = query?.id;
  if (id) {
    loadProduct(id);
  }
});

async function loadProduct(id: string | number) {
  loading.value = true;
  errorText.value = "";
  try {
    const response = await getProductDetail(id);
    product.value = response.data;
    imageFailed.value = false;
  } catch (error) {
    product.value = null;
    errorText.value = "商品加载失败，请稍后重试";
  } finally {
    loading.value = false;
  }
}

function formatPrice(price: string) {
  return Number(price || 0).toFixed(2);
}

function showCartTodo() {
  uni.showToast({ title: "购物车功能开发中", icon: "none" });
}
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef8ff 0%, #f8fcff 46%, #fff 100%);
}

.detail-scroll {
  height: 100vh;
}

.detail-body {
  min-height: 100vh;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));
  box-sizing: border-box;
}

.image-section {
  height: 520rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 34rpx;
  box-sizing: border-box;
  background:
    radial-gradient(circle at 72% 20%, rgba(191, 227, 255, 0.7), transparent 210rpx),
    linear-gradient(180deg, #e8f6ff, #f7fcff);
}

.product-image {
  width: 100%;
  height: 430rpx;
}

.info-card,
.detail-card,
.empty-card {
  margin: 22rpx 30rpx 0;
  padding: 28rpx;
  border: 1rpx solid #e6f0fb;
  border-radius: 30rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16rpx 38rpx rgba(21, 67, 119, 0.08);
}

.price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.price {
  color: #f04f32;
  font-size: 48rpx;
  font-weight: 900;
}

.stock-tag {
  padding: 8rpx 18rpx;
  border: 2rpx solid #28bf61;
  border-radius: 16rpx;
  color: #18a45c;
  font-size: 24rpx;
  font-weight: 850;
}

.stock-tag.empty {
  border-color: #c9d3df;
  color: #8b98a9;
}

.product-name {
  display: block;
  margin-top: 20rpx;
  color: #111827;
  font-size: 36rpx;
  font-weight: 900;
  line-height: 1.32;
}

.product-spec {
  display: block;
  margin-top: 12rpx;
  color: #768298;
  font-size: 26rpx;
}

.card-title {
  color: #111827;
  font-size: 30rpx;
  font-weight: 900;
  margin-bottom: 20rpx;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
}

.detail-item {
  min-width: 0;
  padding: 20rpx;
  border-radius: 20rpx;
  background: #f6fbff;
}

.detail-item.wide {
  grid-column: span 2;
}

.label,
.value {
  display: block;
}

.label {
  color: #8b98a9;
  font-size: 23rpx;
}

.value {
  margin-top: 8rpx;
  overflow-wrap: anywhere;
  color: #1f2937;
  font-size: 27rpx;
  font-weight: 800;
}

.inventory-row {
  display: flex;
  justify-content: space-between;
  padding: 18rpx 0;
  border-bottom: 1rpx solid #edf3f9;
  color: #24304a;
  font-size: 26rpx;
}

.inventory-row:last-child {
  border-bottom: 0;
}

.empty-card {
  min-height: 160rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7c8798;
}

.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 18rpx 30rpx calc(18rpx + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 -10rpx 34rpx rgba(21, 67, 119, 0.08);
}

.cart-button {
  height: 88rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #1476ff, #1f8cff);
  color: #fff;
  font-size: 30rpx;
  font-weight: 900;
  line-height: 88rpx;
}

.button-tap {
  transform: scale(0.98);
  opacity: 0.88;
}

button::after {
  border: 0;
}
</style>

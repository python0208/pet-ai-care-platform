<template>
  <view class="placeholder-page">
    <image class="placeholder-icon" src="/static/icons/png/profile_smile.png" mode="aspectFit" />
    <text class="placeholder-title">我的</text>
    <text class="placeholder-text">Phase 0 仅初始化页面入口</text>
  </view>
</template>

<style scoped>
.placeholder-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  background: #f4f9ff;
}

.placeholder-icon {
  width: 112rpx;
  height: 112rpx;
}

.placeholder-title {
  color: #10172d;
  font-size: 36rpx;
  font-weight: 800;
}

.placeholder-text {
  color: #7d8799;
  font-size: 26rpx;
}
</style>

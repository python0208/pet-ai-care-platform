export function hasToken() {
  return Boolean(uni.getStorageSync("access_token"));
}

export function requireAuth() {
  if (hasToken()) {
    return true;
  }

  uni.navigateTo({
    url: "/pages/auth/index",
  });
  return false;
}

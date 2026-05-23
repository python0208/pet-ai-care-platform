export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  data?: object;
  loading?: boolean;
  auth?: boolean;
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export function request<T>(url: string, options: RequestOptions = {}) {
  const token = uni.getStorageSync("access_token");

  if (options.loading) {
    uni.showLoading({ title: "加载中", mask: true });
  }

  return new Promise<ApiResponse<T>>((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}${url}`,
      method: options.method || "GET",
      data: options.data,
      header: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (response) => {
        const body = response.data as ApiResponse<T>;

        if (response.statusCode === 401) {
          uni.removeStorageSync("access_token");
          uni.removeStorageSync("refresh_token");
        }

        if (response.statusCode >= 200 && response.statusCode < 300 && body.code === 0) {
          resolve(body);
          return;
        }

        reject(body || response);
      },
      fail: reject,
      complete: () => {
        if (options.loading) {
          uni.hideLoading();
        }
      },
    });
  });
}

export function getHealthStatus() {
  return request<{ status: string }>("/health/");
}

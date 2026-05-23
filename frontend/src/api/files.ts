import { API_ORIGIN } from "@/api/request";

export interface UploadFileData {
  id: number;
  url: string;
  file_type: string;
}

export interface UploadFileResponse {
  code: number;
  message: string;
  data: UploadFileData;
  errors?: unknown;
}

export function uploadFile(filePath: string, fileType = "pet") {
  const token = uni.getStorageSync("access_token");

  return new Promise<UploadFileData>((resolve, reject) => {
    uni.uploadFile({
      url: `${API_ORIGIN}/api/files/upload/`,
      filePath,
      name: "file",
      formData: {
        file_type: fileType,
      },
      header: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (response) => {
        let body: UploadFileResponse | null = null;
        try {
          body = JSON.parse(response.data) as UploadFileResponse;
        } catch (error) {
          reject(response);
          return;
        }

        if (response.statusCode >= 200 && response.statusCode < 300 && body.code === 0) {
          resolve(body.data);
          return;
        }
        reject(body);
      },
      fail: reject,
    });
  });
}

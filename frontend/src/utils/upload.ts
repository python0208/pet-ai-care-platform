import { uploadFile } from "@/api/files";

export async function choosePetAvatar() {
  const chooseResult = await new Promise<UniApp.ChooseImageSuccessCallbackResult>(
    (resolve, reject) => {
      uni.chooseImage({
        count: 1,
        sizeType: ["compressed"],
        sourceType: ["album", "camera"],
        success: resolve,
        fail: reject,
      });
    },
  );

  const filePath = chooseResult.tempFilePaths[0];
  if (!filePath) {
    throw new Error("未选择图片");
  }
  return filePath;
}

export async function uploadPetAvatar(filePath: string) {
  uni.showLoading({ title: "上传中...", mask: true });
  try {
    const uploaded = await uploadFile(filePath, "pet");
    return uploaded.url;
  } finally {
    uni.hideLoading();
  }
}

export async function chooseAndUploadPetAvatar() {
  const filePath = await choosePetAvatar();
  const url = await uploadPetAvatar(filePath);
  return { previewPath: filePath, url };
}

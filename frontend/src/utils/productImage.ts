import { resolveMediaUrl } from "@/api/request";
import type { Product } from "@/types/shop";

export const DEFAULT_PRODUCT_IMAGE = "/static/images/default-product.svg";

export function resolveProductImage(product?: Pick<Product, "cover_image" | "cover_image_url"> | null) {
  const imageUrl = product?.cover_image_url || product?.cover_image;
  if (!imageUrl) {
    return DEFAULT_PRODUCT_IMAGE;
  }
  const localhostMediaPath = imageUrl.match(/^https?:\/\/(?:127\.0\.0\.1|localhost)(?::\d+)?(\/media\/.+)$/i);
  if (localhostMediaPath) {
    return resolveMediaUrl(localhostMediaPath[1]) || DEFAULT_PRODUCT_IMAGE;
  }
  if (imageUrl.startsWith("products/")) {
    return resolveMediaUrl(`/media/${imageUrl}`) || DEFAULT_PRODUCT_IMAGE;
  }
  if (imageUrl.startsWith("media/")) {
    return resolveMediaUrl(`/${imageUrl}`) || DEFAULT_PRODUCT_IMAGE;
  }
  return resolveMediaUrl(imageUrl) || DEFAULT_PRODUCT_IMAGE;
}

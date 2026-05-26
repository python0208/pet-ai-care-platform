import { request } from "@/api/request";
import type { PaginatedProducts, ProductCategory, ProductDetail, ProductQuery } from "@/types/shop";

function toQuery(params: ProductQuery = {}) {
  const entries = Object.entries(params).filter(([, value]) => value !== undefined && value !== "");
  if (!entries.length) {
    return "";
  }
  const query = entries
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join("&");
  return `?${query}`;
}

export function getProductCategories() {
  return request<ProductCategory[]>("/shop/categories/");
}

export function getProducts(params: ProductQuery = {}) {
  return request<PaginatedProducts>(`/shop/products/${toQuery(params)}`);
}

export function getProductDetail(id: number | string) {
  return request<ProductDetail>(`/shop/products/${id}/`);
}

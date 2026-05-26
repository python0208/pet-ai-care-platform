export interface ProductCategory {
  id: number;
  name: string;
  parent: number | null;
  sort_order: number;
  is_active: boolean;
}

export interface ProductInventory {
  store_code: string;
  store_display_name: string;
  stock_quantity: number;
}

export interface Product {
  id: number;
  name: string;
  unit: string;
  spec: string;
  barcode: string;
  category: ProductCategory | null;
  retail_price: string;
  weight: string | null;
  shelf_life_months: number | null;
  cover_image: string;
  cover_image_url: string;
  total_stock: number;
  stock_status: "in_stock" | "out_of_stock";
  status: "draft" | "active" | "inactive";
}

export interface ProductDetail extends Product {
  inventories: ProductInventory[];
  created_at: string;
  updated_at: string;
}

export interface PaginatedProducts {
  count: number;
  page: number;
  page_size: number;
  total_pages?: number;
  has_next?: boolean;
  has_previous?: boolean;
  results: Product[];
}

export interface ProductQuery {
  q?: string;
  category_id?: number | string;
  barcode?: string;
  page?: number;
  page_size?: number;
  sort?: "price_asc" | "price_desc" | "newest";
}

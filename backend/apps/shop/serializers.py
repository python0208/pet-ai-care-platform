from django.conf import settings
from django.db.models import Sum
from django.core.files.storage import default_storage
from rest_framework import serializers

from apps.shop.models import Product, ProductCategory, ProductInventory

PRODUCT_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def _product_image_candidates(barcode):
    if not barcode:
        return []
    safe_barcode = str(barcode).strip()
    if not safe_barcode:
        return []
    return [f"products/{safe_barcode}{extension}" for extension in PRODUCT_IMAGE_EXTENSIONS]


def _storage_path_from_media_url(path):
    normalized = str(path).strip().replace("\\", "/")
    if not normalized:
        return ""
    if "/media/" in normalized:
        normalized = normalized[normalized.index("/media/") + len("/media/") :]
    elif normalized.startswith("media/"):
        normalized = normalized[len("media/") :]
    elif normalized.startswith("/media/"):
        normalized = normalized[len("/media/") :]
    elif normalized.startswith("/"):
        normalized = normalized.lstrip("/")
    return normalized


def _find_existing_product_image(barcode):
    for candidate in _product_image_candidates(barcode):
        if default_storage.exists(candidate):
            return candidate
    return ""


def _build_absolute_media_url(request, storage_path):
    if not storage_path:
        return ""
    media_url = settings.MEDIA_URL.rstrip("/") or "/media"
    path = f"{media_url}/{storage_path.lstrip('/')}"
    return request.build_absolute_uri(path) if request else path


def build_cover_image_url(request, cover_image, barcode=None):
    if not cover_image:
        return _build_absolute_media_url(request, _find_existing_product_image(barcode))

    raw_path = str(cover_image).strip().replace("\\", "/")
    if not raw_path:
        return _build_absolute_media_url(request, _find_existing_product_image(barcode))
    if raw_path.startswith(("http://", "https://")):
        return raw_path

    media_url = settings.MEDIA_URL.rstrip("/") or "/media"
    if "/media/" in raw_path:
        path = raw_path[raw_path.index("/media/") :]
    elif raw_path.startswith("media/"):
        path = f"/{raw_path}"
    elif raw_path.startswith("/products/"):
        path = f"{media_url}{raw_path}"
    elif raw_path.startswith("products/"):
        path = f"{media_url}/{raw_path}"
    elif raw_path.startswith("/"):
        path = raw_path
    else:
        path = f"{media_url}/{raw_path.lstrip('/')}"

    storage_path = _storage_path_from_media_url(path)
    if storage_path and default_storage.exists(storage_path):
        return request.build_absolute_uri(path) if request else path

    fallback_storage_path = _find_existing_product_image(barcode)
    if fallback_storage_path:
        return _build_absolute_media_url(request, fallback_storage_path)
    return ""


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ("id", "name", "parent", "sort_order", "is_active")


class ProductInventorySerializer(serializers.ModelSerializer):
    store_display_name = serializers.CharField(read_only=True)

    class Meta:
        model = ProductInventory
        fields = ("store_code", "store_display_name", "stock_quantity")


class ProductListSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "unit",
            "spec",
            "barcode",
            "category",
            "retail_price",
            "weight",
            "shelf_life_months",
            "cover_image",
            "cover_image_url",
            "total_stock",
            "stock_status",
            "status",
        )

    def get_cover_image_url(self, obj):
        return build_cover_image_url(self.context.get("request"), obj.cover_image, obj.barcode)

    def get_total_stock(self, obj):
        if hasattr(obj, "total_stock") and obj.total_stock is not None:
            return obj.total_stock
        return obj.inventories.aggregate(total=Sum("stock_quantity"))["total"] or 0

    def get_stock_status(self, obj):
        return "in_stock" if self.get_total_stock(obj) > 0 else "out_of_stock"


class ProductDetailSerializer(ProductListSerializer):
    inventories = ProductInventorySerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            "inventories",
            "created_at",
            "updated_at",
        )

from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html

from apps.shop.models import (
    Product,
    ProductCategory,
    ProductImportBatch,
    ProductImportRow,
    ProductInventory,
)
from apps.shop.services.import_products import import_product_excel


class ProductImportForm(forms.Form):
    file = forms.FileField(label="Excel 文件")

    def clean_file(self):
        file = self.cleaned_data["file"]
        if not file.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("仅支持 .xlsx 文件")
        return file


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "sort_order", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("sort_order", "is_active")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "name",
        "barcode",
        "category",
        "unit",
        "spec",
        "purchase_price",
        "retail_price",
        "weight",
        "shelf_life_months",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("category", "status", "created_at")
    search_fields = ("name", "barcode", "category__name")
    readonly_fields = ("image_preview",)
    fields = (
        "image_preview",
        "name",
        "unit",
        "spec",
        "barcode",
        "category",
        "purchase_price",
        "retail_price",
        "weight",
        "shelf_life_months",
        "status",
        "cover_image",
    )

    @admin.display(description="图片")
    def image_preview(self, obj):
        if not obj.cover_image:
            return "-"
        return format_html(
            '<img src="{}" style="width:56px;height:56px;object-fit:cover;border-radius:8px;" />',
            obj.cover_image,
        )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj:
            fields.append("barcode")
        return fields


@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = ("product", "store_code_display", "stock_quantity", "updated_at")
    list_filter = ("store_code",)
    search_fields = ("product__name", "product__barcode", "store_code")

    @admin.display(description="直营店序号", ordering="store_code")
    def store_code_display(self, obj):
        return obj.store_display_name


class ProductImportRowInline(admin.TabularInline):
    model = ProductImportRow
    extra = 0
    can_delete = False
    readonly_fields = (
        "row_number",
        "product_name",
        "barcode",
        "status",
        "error_message",
        "product",
        "created_at",
    )
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ProductImportBatch)
class ProductImportBatchAdmin(admin.ModelAdmin):
    change_list_template = "admin/shop/productimportbatch/change_list.html"
    list_display = (
        "id",
        "original_filename",
        "status",
        "total_rows",
        "success_count",
        "updated_count",
        "failed_count",
        "image_success_count",
        "image_failed_count",
        "created_by",
        "created_at",
        "completed_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("original_filename", "error_message")
    readonly_fields = (
        "original_filename",
        "total_rows",
        "success_count",
        "updated_count",
        "failed_count",
        "image_success_count",
        "image_failed_count",
        "status",
        "created_by",
        "created_at",
        "completed_at",
        "error_message",
    )
    inlines = [ProductImportRowInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel_view),
                name="shop_product_import_excel",
            )
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        form = ProductImportForm(request.POST or None, request.FILES or None)
        batch = None
        failed_rows = []
        if request.method == "POST" and form.is_valid():
            upload = form.cleaned_data["file"]
            batch = ProductImportBatch.objects.create(
                file=upload,
                original_filename=upload.name,
                created_by=request.user if request.user.is_authenticated else None,
            )
            batch = import_product_excel(batch)
            failed_rows = batch.rows.filter(status=ProductImportRow.Status.FAILED)
            if batch.status == ProductImportBatch.Status.SUCCESS:
                messages.success(request, "商品导入完成")
            elif batch.status == ProductImportBatch.Status.PARTIAL_SUCCESS:
                messages.warning(request, "商品导入完成，部分行失败")
            else:
                messages.error(request, "商品导入失败")
        context = {
            **self.admin_site.each_context(request),
            "title": "商品 Excel 批量导入",
            "form": form,
            "batch": batch,
            "failed_rows": failed_rows,
            "opts": self.model._meta,
        }
        return render(request, "admin/shop/product_import.html", context)

    def response_change(self, request, obj):
        if "_import_excel" in request.POST:
            return redirect(reverse("admin:shop_product_import_excel"))
        return super().response_change(request, obj)


@admin.register(ProductImportRow)
class ProductImportRowAdmin(admin.ModelAdmin):
    list_display = (
        "batch",
        "row_number",
        "product_name",
        "barcode",
        "status",
        "error_message",
        "product",
        "created_at",
    )
    list_filter = ("status", "batch")
    search_fields = ("product_name", "barcode", "error_message")
    readonly_fields = (
        "batch",
        "row_number",
        "product_name",
        "barcode",
        "status",
        "error_message",
        "product",
        "created_at",
    )

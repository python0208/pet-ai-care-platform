from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


def product_import_upload_to(instance, filename):
    return f"imports/products/{filename}"


class ProductCategory(TimeStampedModel):
    name = models.CharField("分类名称", max_length=128, unique=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="父分类",
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    sort_order = models.IntegerField("排序", default=0)
    is_active = models.BooleanField("是否启用", default=True)

    class Meta:
        verbose_name = "商品分类"
        verbose_name_plural = "商品分类"
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="shop_category_parent_name_uniq",
            )
        ]

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        ACTIVE = "active", "上架"
        INACTIVE = "inactive", "下架"

    name = models.CharField("商品名称", max_length=255)
    unit = models.CharField("单位", max_length=32, blank=True)
    spec = models.CharField("规格", max_length=128, blank=True)
    barcode = models.CharField("条码", max_length=64, unique=True)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name="分类",
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    purchase_price = models.DecimalField(
        "进货价",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    retail_price = models.DecimalField("零售价", max_digits=10, decimal_places=2)
    weight = models.DecimalField(
        "重量",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    shelf_life_months = models.PositiveIntegerField("保质期（月）", null=True, blank=True)
    cover_image = models.CharField("商品主图", max_length=500, blank=True)
    status = models.CharField(
        "商品状态",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ["-updated_at", "-created_at"]
        indexes = [
            models.Index(fields=["barcode"], name="shop_product_barcode_idx"),
            models.Index(fields=["status"], name="shop_product_status_idx"),
            models.Index(fields=["category"], name="shop_product_category_idx"),
        ]

    def __str__(self):
        return f"{self.name}({self.barcode})"


class ProductInventory(TimeStampedModel):
    DEFAULT_STORE_CODE = "DEFAULT"

    product = models.ForeignKey(
        Product,
        verbose_name="商品",
        related_name="inventories",
        on_delete=models.CASCADE,
    )
    store_code = models.CharField("直营店序号", max_length=64, default=DEFAULT_STORE_CODE)
    stock_quantity = models.PositiveIntegerField("当前库存", default=0)
    last_imported_at = models.DateTimeField("最后导入时间", null=True, blank=True)
    remark = models.CharField("备注", max_length=255, blank=True)

    class Meta:
        verbose_name = "商品库存"
        verbose_name_plural = "商品库存"
        ordering = ["product_id", "store_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "store_code"],
                name="shop_inventory_product_store_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["store_code"], name="shop_inventory_store_idx"),
        ]

    @property
    def store_display_name(self):
        if self.store_code == self.DEFAULT_STORE_CODE:
            return "默认库存"
        return self.store_code

    def __str__(self):
        return f"{self.product_id}-{self.store_display_name}"


class ProductImportBatch(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "processing", "处理中"
        SUCCESS = "success", "成功"
        FAILED = "failed", "失败"
        PARTIAL_SUCCESS = "partial_success", "部分成功"

    file = models.FileField("原始 Excel 文件", upload_to=product_import_upload_to)
    original_filename = models.CharField("原始文件名", max_length=255)
    total_rows = models.PositiveIntegerField("总数据行数", default=0)
    success_count = models.PositiveIntegerField("新增成功数量", default=0)
    updated_count = models.PositiveIntegerField("更新数量", default=0)
    failed_count = models.PositiveIntegerField("失败数量", default=0)
    image_success_count = models.PositiveIntegerField("图片成功提取数量", default=0)
    image_failed_count = models.PositiveIntegerField("图片提取失败数量", default=0)
    status = models.CharField(
        "状态",
        max_length=32,
        choices=Status.choices,
        default=Status.PROCESSING,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="导入人",
        related_name="product_import_batches",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    completed_at = models.DateTimeField("完成时间", null=True, blank=True)
    error_message = models.TextField("整体错误信息", blank=True)

    class Meta:
        verbose_name = "商品导入批次"
        verbose_name_plural = "商品导入批次"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id}-{self.original_filename}"


class ProductImportRow(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "新增成功"
        UPDATED = "updated", "更新成功"
        FAILED = "failed", "失败"

    batch = models.ForeignKey(
        ProductImportBatch,
        verbose_name="导入批次",
        related_name="rows",
        on_delete=models.CASCADE,
    )
    row_number = models.PositiveIntegerField("Excel 行号")
    product_name = models.CharField("商品名称", max_length=255, blank=True)
    barcode = models.CharField("条码", max_length=64, blank=True)
    status = models.CharField("状态", max_length=20, choices=Status.choices)
    error_message = models.TextField("错误原因", blank=True)
    product = models.ForeignKey(
        Product,
        verbose_name="商品",
        related_name="import_rows",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "商品导入明细"
        verbose_name_plural = "商品导入明细"
        ordering = ["batch_id", "row_number"]
        indexes = [
            models.Index(fields=["batch", "status"], name="shop_imp_row_batch_status_idx"),
            models.Index(fields=["barcode"], name="shop_imp_row_barcode_idx"),
        ]

    def __str__(self):
        return f"{self.batch_id}-{self.row_number}-{self.status}"

from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from openpyxl import Workbook
from PIL import Image

from apps.shop.models import (
    Product,
    ProductCategory,
    ProductImportBatch,
    ProductImportRow,
    ProductInventory,
)
from apps.shop.services.import_products import (
    import_product_excel,
    normalize_barcode,
    normalize_store_code,
    parse_decimal,
    parse_int,
    save_product_image,
)
from apps.users.models import User


HEADERS = [
    "图片",
    "名称",
    "单位",
    "进货价",
    "规格",
    "零售价",
    "条码",
    "重量",
    "直营店序号",
    "分类",
    "保质期（月）",
    "当前库存",
]


def workbook_file(rows):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(HEADERS)
    for row in rows:
        worksheet.append(row)
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output.getvalue()


class ProductImportParserTests(TestCase):
    def test_normalize_barcode_from_number_and_decimal_text(self):
        self.assertEqual(normalize_barcode(6922298207227), "6922298207227")
        self.assertEqual(normalize_barcode("6922298207227.0"), "6922298207227")

    def test_parse_decimal_values(self):
        self.assertEqual(str(parse_decimal("11.33", "进货价")), "11.33")
        self.assertEqual(str(parse_decimal(55, "零售价")), "55.00")
        self.assertEqual(str(parse_decimal("0.60", "重量")), "0.60")

    def test_parse_int_values(self):
        self.assertEqual(parse_int("681", "当前库存"), 681)
        self.assertEqual(parse_int(710, "当前库存"), 710)
        self.assertEqual(parse_int("913.0", "当前库存"), 913)

    def test_normalize_store_code_defaults_and_trims(self):
        self.assertEqual(normalize_store_code(None), "DEFAULT")
        self.assertEqual(normalize_store_code("  "), "DEFAULT")
        self.assertEqual(normalize_store_code(" Z-1090 "), "Z-1090")


class ProductExcelImportTests(TestCase):
    def setUp(self):
        self.temp_media = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.temp_media.name)
        self.override.enable()
        self.user = User.objects.create_user(
            email="shop-admin@example.com",
            password="StrongPass123",
            is_staff=True,
        )

    def tearDown(self):
        self.override.disable()
        self.temp_media.cleanup()

    def make_batch(self, rows):
        content = workbook_file(rows)
        upload = SimpleUploadedFile(
            "products.xlsx",
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        return ProductImportBatch.objects.create(
            file=upload,
            original_filename="products.xlsx",
            created_by=self.user,
        )

    def test_import_creates_category_product_and_default_inventory(self):
        batch = self.make_batch(
            [
                [
                    "",
                    "顽皮 全价幼猫粮500g",
                    "袋",
                    "11.33",
                    "500g",
                    "55",
                    "6922298207227",
                    "0.60",
                    "",
                    "猫咪主粮",
                    24,
                    681,
                ]
            ]
        )

        import_product_excel(batch)

        product = Product.objects.get(barcode="6922298207227")
        inventory = ProductInventory.objects.get(product=product)
        batch.refresh_from_db()
        self.assertEqual(product.category.name, "猫咪主粮")
        self.assertEqual(str(product.retail_price), "55.00")
        self.assertEqual(inventory.store_code, "DEFAULT")
        self.assertEqual(inventory.store_display_name, "默认库存")
        self.assertEqual(inventory.stock_quantity, 681)
        self.assertEqual(batch.success_count, 1)
        self.assertEqual(batch.failed_count, 0)

    def test_existing_barcode_updates_product_and_inventory(self):
        category = ProductCategory.objects.create(name="旧分类")
        product = Product.objects.create(
            name="旧商品",
            barcode="6922298207227",
            category=category,
            retail_price="20.00",
        )
        ProductInventory.objects.create(product=product, store_code="Z-1090", stock_quantity=1)
        batch = self.make_batch(
            [
                [
                    "",
                    "顽皮 全价幼猫粮500g",
                    "袋",
                    "11.33",
                    "500g",
                    "55",
                    "6922298207227",
                    "0.60",
                    " Z-1090 ",
                    "猫咪主粮",
                    24,
                    710,
                ]
            ]
        )

        import_product_excel(batch)

        product.refresh_from_db()
        inventory = ProductInventory.objects.get(product=product, store_code="Z-1090")
        batch.refresh_from_db()
        self.assertEqual(product.name, "顽皮 全价幼猫粮500g")
        self.assertEqual(product.category.name, "猫咪主粮")
        self.assertEqual(inventory.stock_quantity, 710)
        self.assertEqual(batch.updated_count, 1)
        self.assertEqual(ProductImportRow.objects.get(batch=batch).status, "updated")

    def test_blank_store_code_reimports_update_default_inventory(self):
        first_batch = self.make_batch(
            [
                [
                    "",
                    "猫粮",
                    "袋",
                    "",
                    "500g",
                    "55",
                    "10001",
                    "",
                    "",
                    "猫咪主粮",
                    "",
                    681,
                ]
            ]
        )
        second_batch = self.make_batch(
            [
                [
                    "",
                    "猫粮",
                    "袋",
                    "",
                    "500g",
                    "60",
                    "10001",
                    "",
                    " ",
                    "猫咪主粮",
                    "",
                    913,
                ]
            ]
        )

        import_product_excel(first_batch)
        import_product_excel(second_batch)

        product = Product.objects.get(barcode="10001")
        inventories = ProductInventory.objects.filter(product=product, store_code="DEFAULT")
        self.assertEqual(inventories.count(), 1)
        self.assertEqual(inventories.get().stock_quantity, 913)

    def test_invalid_row_does_not_block_other_rows(self):
        batch = self.make_batch(
            [
                ["", "猫粮", "袋", "", "500g", "55", "10001", "", "", "猫咪主粮", "", 681],
                ["", "无条码商品", "袋", "", "500g", "55", "", "", "", "猫咪主粮", "", 681],
                ["", "坏库存", "袋", "", "500g", "55", "10002", "", "", "猫咪主粮", "", "abc"],
            ]
        )

        import_product_excel(batch)

        batch.refresh_from_db()
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(batch.success_count, 1)
        self.assertEqual(batch.failed_count, 2)
        self.assertEqual(batch.status, "partial_success")
        self.assertEqual(ProductImportRow.objects.filter(batch=batch, status="failed").count(), 2)

    def test_save_product_image_returns_media_products_path(self):
        image = Image.new("RGB", (8, 8), color="white")
        output = BytesIO()
        image.save(output, format="PNG")

        url = save_product_image(output.getvalue(), barcode="6922298207227")

        self.assertEqual(url, "/media/products/6922298207227.png")


class ProductImportAdminTests(TestCase):
    def test_non_staff_user_cannot_access_import_page(self):
        user = User.objects.create_user(
            email="normal-user@example.com",
            password="StrongPass123",
        )
        client = Client()
        client.force_login(user)

        response = client.get(reverse("admin:shop_product_import_excel"))

        self.assertEqual(response.status_code, 302)

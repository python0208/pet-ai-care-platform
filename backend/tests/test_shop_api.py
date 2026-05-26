import tempfile
from pathlib import Path

from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.shop.models import Product, ProductCategory, ProductInventory


class ShopProductApiTests(APITestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()
        products_dir = Path(self.media_dir.name) / "products"
        products_dir.mkdir(parents=True, exist_ok=True)
        (products_dir / "6922298207227.png").write_bytes(b"fake image")

        self.cat_food = ProductCategory.objects.create(name="猫咪主粮", sort_order=1)
        self.snack = ProductCategory.objects.create(name="零食", sort_order=2)
        self.inactive_category = ProductCategory.objects.create(name="停用分类", is_active=False)
        self.product = Product.objects.create(
            name="顽皮 全价幼猫粮500g",
            unit="袋",
            spec="500g",
            barcode="6922298207227",
            category=self.cat_food,
            purchase_price="11.33",
            retail_price="55.00",
            weight="0.60",
            shelf_life_months=24,
            cover_image="/media/products/6922298207227.png",
            status=Product.Status.ACTIVE,
        )
        ProductInventory.objects.create(
            product=self.product,
            store_code=ProductInventory.DEFAULT_STORE_CODE,
            stock_quantity=681,
        )
        self.inactive_product = Product.objects.create(
            name="下架商品",
            barcode="inactive001",
            category=self.snack,
            purchase_price="3.00",
            retail_price="9.90",
            status=Product.Status.INACTIVE,
        )

    def tearDown(self):
        self.settings_override.disable()
        self.media_dir.cleanup()

    def test_categories_return_active_only(self):
        response = self.client.get(reverse("shop-categories"))

        self.assertEqual(response.status_code, 200)
        names = [item["name"] for item in response.json()["data"]]
        self.assertEqual(names, ["猫咪主粮", "零食"])

    def test_product_list_returns_active_without_purchase_price(self):
        response = self.client.get(reverse("shop-products"))

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]["results"]
        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertEqual(item["barcode"], "6922298207227")
        self.assertNotIn("purchase_price", item)
        self.assertIn("cover_image_url", item)
        self.assertTrue(item["cover_image_url"].endswith("/media/products/6922298207227.png"))
        self.assertEqual(item["total_stock"], 681)
        self.assertEqual(item["stock_status"], "in_stock")

    def test_product_list_builds_media_url_from_relative_image_path(self):
        self.product.cover_image = "products/relative.png"
        self.product.save(update_fields=["cover_image"])
        (Path(self.media_dir.name) / "products" / "relative.png").write_bytes(b"fake image")

        response = self.client.get(reverse("shop-products"))

        item = response.json()["data"]["results"][0]
        self.assertTrue(item["cover_image_url"].endswith("/media/products/relative.png"))

    def test_product_list_does_not_expose_local_filesystem_image_path(self):
        self.product.cover_image = r"D:\demo\media\products\local.png"
        self.product.save(update_fields=["cover_image"])
        (Path(self.media_dir.name) / "products" / "local.png").write_bytes(b"fake image")

        response = self.client.get(reverse("shop-products"))

        item = response.json()["data"]["results"][0]
        self.assertTrue(item["cover_image_url"].endswith("/media/products/local.png"))
        self.assertNotIn("D:", item["cover_image_url"])

    def test_product_list_falls_back_to_barcode_jpg_when_image_is_empty(self):
        self.product.cover_image = ""
        self.product.save(update_fields=["cover_image"])
        (Path(self.media_dir.name) / "products" / "6922298207227.jpg").write_bytes(b"fake image")

        response = self.client.get(reverse("shop-products"))

        item = response.json()["data"]["results"][0]
        self.assertTrue(item["cover_image_url"].endswith("/media/products/6922298207227.jpg"))

    def test_product_list_falls_back_to_barcode_jpg_when_image_file_missing(self):
        self.product.cover_image = "products/missing.png"
        self.product.save(update_fields=["cover_image"])
        (Path(self.media_dir.name) / "products" / "6922298207227.jpg").write_bytes(b"fake image")

        response = self.client.get(reverse("shop-products"))

        item = response.json()["data"]["results"][0]
        self.assertTrue(item["cover_image_url"].endswith("/media/products/6922298207227.jpg"))

    def test_product_list_returns_empty_image_url_when_no_file_exists(self):
        self.product.cover_image = ""
        self.product.barcode = "noimage001"
        self.product.save(update_fields=["cover_image", "barcode"])

        response = self.client.get(reverse("shop-products"))

        item = response.json()["data"]["results"][0]
        self.assertEqual(item["cover_image_url"], "")

    def test_product_list_pagination_includes_next_state(self):
        for index in range(25):
            Product.objects.create(
                name=f"测试商品{index}",
                barcode=f"page{index}",
                category=self.cat_food,
                retail_price="9.90",
                status=Product.Status.ACTIVE,
            )

        response = self.client.get(reverse("shop-products"), {"page": 1, "page_size": 10})

        data = response.json()["data"]
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 10)
        self.assertEqual(len(data["results"]), 10)
        self.assertTrue(data["has_next"])
        self.assertEqual(data["total_pages"], 3)

    def test_product_list_second_page_uses_page_size(self):
        for index in range(12):
            Product.objects.create(
                name=f"第二页商品{index}",
                barcode=f"second{index}",
                category=self.cat_food,
                retail_price="9.90",
                status=Product.Status.ACTIVE,
            )

        response = self.client.get(reverse("shop-products"), {"page": 2, "page_size": 10})

        data = response.json()["data"]
        self.assertEqual(data["page"], 2)
        self.assertEqual(data["page_size"], 10)
        self.assertGreaterEqual(len(data["results"]), 1)
        self.assertTrue(data["has_previous"])

    def test_product_list_filters_by_category(self):
        response = self.client.get(reverse("shop-products"), {"category_id": self.snack.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["count"], 0)

    def test_product_list_searches_by_name_and_barcode(self):
        response = self.client.get(reverse("shop-products"), {"q": "幼猫粮"})
        self.assertEqual(response.json()["data"]["count"], 1)

        response = self.client.get(reverse("shop-products"), {"q": "6922298207227"})
        self.assertEqual(response.json()["data"]["count"], 1)

    def test_product_detail_returns_inventory_without_purchase_price(self):
        response = self.client.get(reverse("shop-product-detail", args=[self.product.id]))

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["name"], "顽皮 全价幼猫粮500g")
        self.assertNotIn("purchase_price", data)
        self.assertTrue(data["cover_image_url"].endswith("/media/products/6922298207227.png"))
        self.assertEqual(data["inventories"][0]["store_display_name"], "默认库存")
        self.assertEqual(data["total_stock"], 681)

    def test_inactive_product_detail_is_not_visible(self):
        response = self.client.get(reverse("shop-product-detail", args=[self.inactive_product.id]))

        self.assertEqual(response.status_code, 404)

    def test_common_user_cannot_modify_product_api(self):
        response = self.client.post(
            reverse("shop-products"),
            {"name": "非法创建"},
            format="json",
        )

        self.assertEqual(response.status_code, 405)

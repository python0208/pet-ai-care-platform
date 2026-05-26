from django.urls import path

from apps.shop.views import ProductCategoryListView, ProductDetailView, ProductListView

urlpatterns = [
    path("shop/categories/", ProductCategoryListView.as_view(), name="shop-categories"),
    path("shop/products/", ProductListView.as_view(), name="shop-products"),
    path("shop/products/<int:pk>/", ProductDetailView.as_view(), name="shop-product-detail"),
]

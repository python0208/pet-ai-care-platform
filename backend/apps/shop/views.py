from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.views import APIView

from apps.common.pagination import StandardResultsSetPagination
from apps.common.responses import success_response
from apps.shop.models import Product, ProductCategory
from apps.shop.serializers import (
    ProductCategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class ProductCategoryListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = ProductCategory.objects.filter(is_active=True).order_by("sort_order", "id")
        return success_response(ProductCategorySerializer(categories, many=True).data)


class ProductListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self, request):
        queryset = (
            Product.objects.filter(status=Product.Status.ACTIVE)
            .select_related("category")
            .annotate(total_stock=Sum("inventories__stock_quantity"))
        )
        q = request.query_params.get("q", "").strip()
        category_id = request.query_params.get("category_id", "").strip()
        barcode = request.query_params.get("barcode", "").strip()
        sort = request.query_params.get("sort", "").strip()

        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(barcode__icontains=q))
        if category_id and category_id.isdigit():
            queryset = queryset.filter(category_id=category_id)
        if barcode:
            queryset = queryset.filter(barcode=barcode)

        if sort == "price_asc":
            return queryset.order_by("retail_price", "-updated_at")
        if sort == "price_desc":
            return queryset.order_by("-retail_price", "-updated_at")
        if sort == "newest":
            return queryset.order_by("-created_at")
        return queryset.order_by("-updated_at", "-created_at")

    def get(self, request):
        queryset = self.get_queryset(request)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        product = get_object_or_404(
            Product.objects.filter(status=Product.Status.ACTIVE)
            .select_related("category")
            .prefetch_related("inventories")
            .annotate(total_stock=Sum("inventories__stock_quantity")),
            pk=pk,
        )
        return success_response(ProductDetailSerializer(product, context={"request": request}).data)

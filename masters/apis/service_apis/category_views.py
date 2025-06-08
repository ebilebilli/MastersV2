from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from services.models.category_model import Category
from services.serializers.category_serializer import CategorySerializer
from utils.paginations import CustomPagination
from users.models.master_model import Master
from users.serializers.master_serializer import MasterSerializer

__all__ = [
    'CategoryListAPIView',
    'MasterListForCategoryAPIView',
]


class CategoryListAPIView(APIView):
    """
    get:
    Retrieve a list of all available service categories.

    This endpoint returns all categories from the database.
    
    Returns:
    - 200 OK with a list of categories.
    - 404 Not Found if no categories exist.
    """
    permission_classes = [AllowAny]
    http_method_names = ['get']
    
    @swagger_auto_schema(
        operation_summary="Kateqoriyalari qaytarır",
        responses={200: CategorySerializer(many=True)}
    )

    def get(self, request):
        cache_key = f'category_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            cache.set(cache_key, serializer.data, timeout=settings.TIMEOUT)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'error': 'Heç bir kategoriya tapılmadı'}, status=status.HTTP_404_NOT_FOUND)


class MasterListForCategoryAPIView(APIView):
    """
    get:
    Retrieve a paginated list of active masters for a given category.

    This endpoint returns all active masters associated with the specified category ID.
    Pagination is applied to the result set.

    Path Parameters:
    - category_id (int): The ID of the category.

    Returns:
    - 200 OK with a paginated list of active masters.
    - 404 Not Found if the category or any matching master is not found.
    """
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    http_method_names = ['get']
    
    @swagger_auto_schema(
        operation_summary="Kateqoriya üzrə aktiv ustaları qaytarır",
        responses={200: MasterSerializer(many=True)}
    )

    def get(self, request, category_id):
        pagination = self.pagination_class()
        category = get_object_or_404(Category, id=category_id)
        masters = Master.objects.filter(profession_category=category, is_active_on_main_page=True)
        if not masters.exists():
            return Response({
                'error': 'Hal-hazırda bu kateqoriyaya uyğun aktiv bir usta yoxdur'
            }, status=status.HTTP_404_NOT_FOUND)
        result_page = pagination.paginate_queryset(masters, request)
        serializer = MasterSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)
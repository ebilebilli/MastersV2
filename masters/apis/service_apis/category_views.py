from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

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
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def get(self, request):
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'error': 'Heç bir kategoriya tapılmadı'})


class MasterListForCategoryAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class =  CustomPagination

    def get(self, request, category_id):
        pagination = self.pagination_class()
        category = get_object_or_404(Category, id=category_id)
        masters =  Master.objects.filter(profession_category=category, is_active_on_main_page=True)
        if not masters.exists():
            return Response({
                'error': 'Hal-hazırda bu kateqoriyaya uyğun aktif bir usta yoxdur'
            },status=status.HTTP_404_NOT_FOUND)
        result_page = pagination.paginate_queryset(masters, request)
        serializer = MasterSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)

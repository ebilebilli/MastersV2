from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.conf import settings

from services.models.category_model import Category
from services.models.service_model import Service
from services.serializers.service_serializer import ServiceSerializer
from users.models.master_model import Master
from users.serializers.master_serializer import MasterSerializer
from utils.paginations import CustomPagination


__all__ = [
    'ServicesForCategoryAPIView',
    'MasterListForServicesAPIView'
]

class ServicesForCategoryAPIView(APIView):
    """
    get:
    Retrieve a list of services associated with a given category.

    Path Parameters:
    - category_id (int): The ID of the category.

    Returns:
    - 200 OK with a list of services.
    - 404 Not Found if the category does not exist.
    """
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def get(self, request, category_id):
        cache_key = f'services_for_category_{category_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
      
        category = get_object_or_404(Category, id=category_id)
        services = Service.objects.filter(category=category)
        serializer = ServiceSerializer(services, many=True)
        cache.set(cache_key, serializer.data, timeout=settings.TIMEOUT)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
    

class MasterListForServicesAPIView(APIView):
    """
    get:
    Retrieve a paginated list of active masters for a given service.

    Path Parameters:
    - service_id (int): The ID of the service.

    Returns:
    - 200 OK with a paginated list of active masters.
    - 404 Not Found if the service does not exist or no masters are available.
    """
    permission_classes = [AllowAny]
    pagination_class =  CustomPagination

    def get(self, request, service_id):
        pagination = self.pagination_class()
        service = get_object_or_404(Service, id=service_id)
        masters =  Master.objects.filter(profession_service=service, is_active_on_main_page=True)
        if not masters.exists():
            return Response({
                'error': 'Hal-hazırda bu servisə uyğun aktif bir usta yoxdur'
            },status=status.HTTP_404_NOT_FOUND)
        result_page = pagination.paginate_queryset(masters, request)
        serializer = MasterSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)

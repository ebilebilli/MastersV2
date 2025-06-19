from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.cache import cache
from django.conf import settings

from core.models.city_model import City, District
from core.serializers.city_serializers import CitySerializer, DistrictSerializer


__all__ = [
    'CityListAPIView',
    'DistrictListAPIView'
]


class CityListAPIView(APIView):
    """
    get:
    Returns a list of all cities.

    This endpoint retrieves all `City` objects from the database and returns them in JSON format.
    """
    permission_classes = [AllowAny]
    http_method_names = ['get']
    
    @swagger_auto_schema(
        operation_summary="Get all cities",
        operation_description="Returns a list of all cities in JSON format.",
        responses={
            200: CitySerializer(many=True),
            404: openapi.Response('No cities found.'),
            500: openapi.Response('Internal server error.')
        }
    )
    def get(self, request):
        cache_key = f'city_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        cache.set(cache_key, serializer.data, timeout=settings.TIMEOUT)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class DistrictListAPIView(APIView):
    """
    get:
    Returns a list of all districts.

    This endpoint retrieves all `District` objects from the database and returns them in JSON format.
    """
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def get(self, request):
        cache_key = f'district_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        
        districts = District.objects.all()
        serializer = DistrictSerializer(districts, many=True)
        cache.set(cache_key, serializer.data, timeout=settings.TIMEOUT)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        

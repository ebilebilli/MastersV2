from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.conf import settings

from core.models.city_model import City, District
from core.serializers.city_serializers import CitySerializer, DistrictSerializer


class CityListAPIView(APIView):
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
        cache_key = 'city_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        try:
            cities = City.objects.all()
            if not cities.exists():
                return Response({'error': 'No cities found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = CitySerializer(cities, many=True)
            cache.set(cache_key, serializer.data, timeout=settings.TIMEOUT)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DistrictListAPIView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ['get']

    @swagger_auto_schema(
        operation_summary="Get all districts",
        operation_description="Returns a list of all districts in JSON format.",
        responses={
            200: DistrictSerializer(many=True),
            404: openapi.Response('No districts found.'),
            500: openapi.Response('Internal server error.')
        }
    )
    def get(self, request):
        cache_key = 'district_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        try:
            districts = District.objects.all()
            if not districts.exists():
                return Response({'error': 'No districts found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = DistrictSerializer(districts, many=True)
            cache.set(cache_key, serializer.data, timeout=settings.TIMEOUT)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

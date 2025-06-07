from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

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

    def get(self, request):
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
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
        districts = District.objects.all()
        serializer = DistrictSerializer(districts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        

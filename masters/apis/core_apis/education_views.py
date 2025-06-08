from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.conf import settings

from core.models.education_model import Education
from core.serializers.education_serializer import EducationSerializer


__all__ = [
    'EducationListAPIView'
]

class EducationListAPIView(APIView):
    """
    get:
    Returns a list of all education entries.

    This endpoint retrieves all `Education` objects from the database
    and returns them serialized in JSON format.
    """
    permission_classes = [AllowAny]
    http_method_names = ['get']

    @swagger_auto_schema(
        operation_description="Returns a list of all education entries.",
        responses={200: EducationSerializer(many=True)}
    )
    def get(self, request):
        cache_key = f'education_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        
        educations = Education.objects.all()
        serializer = EducationSerializer(educations, many=True)
        cache.set(cache_key, serializer.data, timeout=settings.TIMEOUT)
        return Response(serializer.data, status=status.HTTP_200_OK)

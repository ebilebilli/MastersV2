from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.conf import settings

from core.models.language_model import Language
from core.serializers.language_serializer import LanguageSerializer


__all__ = [
    'LanguageListAPIView'
]

class LanguageListAPIView(APIView):
    """
    get:
    Returns a list of all languages.

    This endpoint retrieves all `Language` objects from the database
    and returns them serialized in JSON format.
    """
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def get(self, request):
        cache_key = f'language_list'
        cached_data = cache.set(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        
        languages = Language.objects.all()
        serializer = LanguageSerializer(languages, many=True)
        cache.set(cache_key, serializer.data, timeout=settings.TIMEOUT)
        return Response(serializer.data, status=status.HTTP_200_OK)



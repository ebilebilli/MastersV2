from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from core.models.language_model import Language
from core.serializers.language_serializer import LanguageSerializer


__all__ = [
    'LanguageListAPIView'
]

class LanguageListAPIView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def get(self, request):
        languages = Language.objects.all()
        serializer = LanguageSerializer(languages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



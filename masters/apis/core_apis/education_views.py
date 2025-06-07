from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

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

    def get(self, request):
        educations = Education.objects.all()
        serializer = EducationSerializer(educations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.models.master_model import Master
from users.models.master_work_img_model import MasterWorkImage
from users.serializers.master_image_serializer import MasterImageSerializer
from utils.permissions import HeHasPermission

__all__ = [
    'WorkImagesForMasterAPIView',
    'DeleteMasterWorkImageAPIView',
]


class WorkImagesForMasterAPIView(APIView):
    """
    get:
    Retrieve a list of work images for a specific master.

    post:
    Upload one or more new work images for the authenticated master.
    Limits the total image count to 10.
    """
    parser_classes = [JSONParser, MultiPartParser]
    http_method_names = ['get', 'post']
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Müəyyən bir usta üçün iş şəkillərinin siyahısını əldə edin.",
        responses={
            200: MasterImageSerializer(many=True),
            404: openapi.Response(description="Usta tapılmadı.")
        },
        manual_parameters=[
            openapi.Parameter('master_id', openapi.IN_PATH, description="Ustanın ID-si", type=openapi.TYPE_INTEGER, required=True)
        ]
    )
    def get(self, request, master_id):
        master = get_object_or_404(Master, is_active_on_main_page=True, id=master_id)
        images = MasterWorkImage.objects.filter(master=master)
        serializer = MasterImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Authentifikasiya olunmuş usta üçün bir və ya daha çox yeni iş şəkli yükləyin (maksimum 10 şəkil).",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=MasterImageSerializer,
            description="Şəkil məlumatları (bir və ya bir neçə şəkil)"
        ),
        responses={
            201: MasterImageSerializer(many=True),
            400: openapi.Response(description="Daxil edilən məlumatlar səhvdir və ya şəkil limiti keçilib."),
            401: openapi.Response(description="İcazəsiz giriş."),
            404: openapi.Response(description="Usta tapılmadı.")
        },
        manual_parameters=[
            openapi.Parameter('master_id', openapi.IN_PATH, description="Ustanın ID-si", type=openapi.TYPE_INTEGER, required=True)
        ]
    )
    def post(self, request, master_id):
        try:
            master = get_object_or_404(Master, is_active_on_main_page=True, id=master_id)
            user = request.user
            if user != master:
                return Response({'error': 'İcazəniz yoxdur'}, status=status.HTTP_401_UNAUTHORIZED)
            
        except Master.DoesNotExist:
            return Response({'error': 'Usta tapılmadı.'}, status=status.HTTP_404_NOT_FOUND)

        existing_image_count = MasterWorkImage.objects.filter(master=master).count()
        incoming_data = request.data
        new_images = incoming_data if isinstance(incoming_data, list) else [incoming_data]
        new_count = len(new_images)

        if existing_image_count + new_count > 10:
            return Response(
                {
                    'error': f'Usta maksimum 10 şəkil yükləyə bilər. Hal-hazırda {existing_image_count} şəkli var, sən {new_count} əlavə etmək istəyirsən.'
                }, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = MasterImageSerializer(data=new_images, many=isinstance(incoming_data, list))
        if serializer.is_valid():
            serializer.save(master=master)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteMasterWorkImageAPIView(APIView):
    """
    delete:
    Delete a master work image by its ID.

    Path Parameters:
    - image_id (int): The ID of the image to delete.

    Returns:
    - 204 No Content if deleted.
    - 400 Bad Request if image not found.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HeHasPermission]
    http_method_names = ['delete']

    @swagger_auto_schema(
        operation_description="Ustanın iş şəklini ID ilə silin (yalnız icazəsi olan istifadəçilər).",
        responses={
            204: openapi.Response(description="Şəkil uğurla silindi."),
            400: openapi.Response(description="Şəkil tapılmadı."),
            401: openapi.Response(description="İcazəsiz giriş.")
        },
        manual_parameters=[
            openapi.Parameter('image_id', openapi.IN_PATH, description="Şəklin ID-si", type=openapi.TYPE_INTEGER, required=True)
        ]
    )
    def delete(self, request, image_id):
        try:
            image = MasterWorkImage.objects.get(id=image_id)
            image.delete()
            return Response({'message': 'Şəkil silindi'}, status=status.HTTP_204_NO_CONTENT)
        except MasterWorkImage.DoesNotExist:
            return Response({'error': 'Şəkil tapılmadı'}, status=status.HTTP_400_BAD_REQUEST)
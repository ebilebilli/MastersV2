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
    'CreateWorkImagesForMasterAPIView',
    'DeleteMasterWorkImageAPIView'
]


class WorkImagesForMasterAPIView(APIView):
    """
    get:
    Retrieve a list of work images for a specific master.

    post:
    Upload one or more new work images for the authenticated master.
    Limits the total image count to 10.
    """
    http_method_names = ['get']
    
    @swagger_auto_schema(
        operation_summary="Masterin iş şəkillərini göstər",
        responses={200: MasterImageSerializer(many=True)}
    )
    
    def get(self, request, master_id):
        master = get_object_or_404(Master, is_active_on_main_page=True, id=master_id)
        images = MasterWorkImage.objects.filter(master=master)
        serializer = MasterImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateWorkImagesForMasterAPIView(APIView):
    """
    Upload work images for a master.

    Authenticated users can upload up to 10 images for their own master profile. 
    Only the owner of the profile can upload images. Supports single or multiple uploads.

    Returns 201 on success, 400 if image limit is exceeded or data is invalid,
    401 if not authorized, and 404 if master not found.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HeHasPermission]
    parser_classes = [JSONParser, MultiPartParser]
    http_method_names = ['post']


    @swagger_auto_schema(
        operation_summary="Master üçün şəkil yüklə",
        request_body=MasterImageSerializer(many=True),
        responses={201: MasterImageSerializer(many=True), 400: 'Validasiya xətası'}
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
    permission_classes = [HeHasPermission]
    http_method_names = ['delete']
    
    @swagger_auto_schema(
        operation_summary="Şəkli sil (master)",
        responses={
            204: openapi.Response(description="Şəkil silindi"),
            400: openapi.Response(description="Şəkil tapılmadı")
        }
    )
    
    def delete(self, request, image_id):
        try:
            image = MasterWorkImage.objects.get(id=image_id)
            image.delete()
            return Response({'message': 'Şəkil silindi'}, status=status.HTTP_204_NO_CONTENT)
        except MasterWorkImage.DoesNotExist:
            return Response({'error': 'Şəkil tapılmadı'}, status=status.HTTP_400_BAD_REQUEST)
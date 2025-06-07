from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser

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

    def get(self, request, master_id):
        master = get_object_or_404(Master, is_active_on_main_page=True, id=master_id)
        images = MasterWorkImage.objects.filter(master=master)
        serializer = MasterImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, master_id):
        try:
            master = get_object_or_404(Master, is_active_on_main_page=True, id=master_id)
            user = request.user
            if user != master:
                return Response({'error': 'İcazəniz yoxdur'})
            
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
                },status=status.HTTP_400_BAD_REQUEST
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

    def delete(self, request, image_id):
        try:
            image = MasterWorkImage.objects.get(id=image_id)
            image.delete()
            return Response({'message: Şəkil silindi'}, status=status.HTTP_204_NO_CONTENT)
        except image.DoesNotExist():
            return Response({'error: Şəkil tapılmadı'}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView, status
from rest_framework.response import Response

from users.models.master_model import Master
from users.models.master_work_img_model import MasterWorkImage
from users.serializers.master_image_serializer import MasterImageSerializer


class WorkImagesForMasterAPIView(APIView):
    def get(self, request, master_id):
        master = Master.objects.get(is_active_on_main_page=True, id=master_id)
        images = MasterWorkImage.objects.filter(master=master)
        serializer = MasterImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, master_id):
        try:
            master = Master.objects.get(is_active_on_main_page=True, id=master_id)
        except Master.DoesNotExist:
            return Response({"detail": "Usta tapılmadı."}, status=status.HTTP_404_NOT_FOUND)

        existing_image_count = MasterWorkImage.objects.filter(master=master).count()
        incoming_data = request.data
        new_images = incoming_data if isinstance(incoming_data, list) else [incoming_data]
        new_count = len(new_images)

        if existing_image_count + new_count > 10:
            return Response(
                {
                    "detail": f"Usta maksimum 10 şəkil yükləyə bilər. Hal-hazırda {existing_image_count} şəkli var, sən {new_count} əlavə etmək istəyirsən."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = MasterImageSerializer(data=new_images, many=isinstance(incoming_data, list))
        if serializer.is_valid():
            serializer.save(master=master)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class DeleteMasterWorkImageAPIView(APIView):
    def delete(self, request, image_id):
        image = MasterWorkImage.objects.get(id=image_id)
        if image:
            image.delete()
            return Response({'message: Sekil silindi'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error: Sekil tapilmadi'}, status=status.HTTP_400_BAD_REQUEST)
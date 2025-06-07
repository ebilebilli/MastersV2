from rest_framework import serializers
from users.models.master_work_img_model import MasterWorkImage


class MasterImageSerializer(serializers.ModelSerializer):
    """
    Serializer for representing a Master's work images.
    
    Includes a custom image_url field that returns the full image URL 
    if the image exists. The `master` field is read-only and represented 
    by its primary key.
    """
    master = serializers.PrimaryKeyRelatedField(read_only=True)  
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = MasterWorkImage
        fields = '__all__'

    def get_image_url(self, obj):
        """
        Returns the URL of the image if it exists.

        Args:
            obj (MasterWorkImage): The instance of the image model.

        Returns:
            str or None: The image URL or None if no image is uploaded.
        """
        if obj.image:
            return obj.image.url
        return None
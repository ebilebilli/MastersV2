from rest_framework import serializers
from models.master_work_img_model import MasterWorkImage


class MasterImageSerializer(serializers.ModelSerializer):
    master = serializers.PrimaryKeyRelatedField(read_only=True)  
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = MasterWorkImage
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
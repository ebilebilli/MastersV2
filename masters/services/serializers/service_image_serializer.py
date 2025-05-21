from rest_framework import serializers
from masters.services.models.service_model_image import ServiceImage
from services.models.service_model import Service


class ServiceImageSerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(read_only=True)  
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceImage
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("An image must be uploaded.")
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image size cannot exceed 5MB.")
        valid_formats = ['image/jpeg', 'image/png']
        if value.content_type not in valid_formats:
            raise serializers.ValidationError("Only JPEG and PNG formats are supported.")
        return value
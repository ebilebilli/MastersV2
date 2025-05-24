from rest_framework import serializers
from users.models import MasterWorkImage


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

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("Şəkil seçin zəhmət olmasa")
        if value.size > 5 * 1024 * 1024:
             raise serializers.ValidationError("Şəkil həcmi 5MB-dan çox olmamalıdır.")
        valid_formats = ['image/jpeg', 'image/png']
        if value.content_type not in valid_formats:
            raise serializers.ValidationError("Şəkil formatı : jpg, png dəstəklənir")
        return value
    
    def update(self, instance, validated_data):
        portfolio_images = validated_data.pop('portfolio_images', [])
        instance = super().update(instance, validated_data)
        for img in portfolio_images:
            MasterWorkImage.objects.create(master=instance, image=img)
        return instance
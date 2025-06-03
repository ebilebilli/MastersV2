from rest_framework import serializers
from reviews.models.review_img_model import ReviewWorkImage


class ReviewImageSerializer(serializers.ModelSerializer):
    master = serializers.PrimaryKeyRelatedField(read_only=True)  
    image_url = serializers.SerializerMethodField()

    class Meta:
        model =  ReviewWorkImage
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    

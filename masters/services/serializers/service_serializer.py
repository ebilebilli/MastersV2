from rest_framework import serializers

from services.models.service_model import ServiceTemplate
from services.models.category_model import Category
from users.models.customeruser_model import Master
from core.models.city_model import City
from .service_image_serializer import ServiceImageSerializer


class ServiceTemplateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
    queryset=Category.objects.all(),
    slug_field='name'
    )
   
    class Meta:
        model = ServiceTemplate
        fields = '__all__'


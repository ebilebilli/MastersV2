from rest_framework import serializers

from services.models.service_model import Service
from services.models.category_model import Category


class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
    queryset=Category.objects.all(),
    slug_field='name'
    )
    
    class Meta:
        model = Service
        fields = '__all__'


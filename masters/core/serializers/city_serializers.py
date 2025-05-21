from rest_framework import serializers
from core.models.city_model import City


class CitySerializer(serializers.ModelSerializer):  
    class Meta:
        model = City
        fields = '__all__'
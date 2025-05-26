from rest_framework import serializers
from core.models.city_model import City, District


class CitySerializer(serializers.ModelSerializer):  
    class Meta:
        model = City
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'display_name', 'city']
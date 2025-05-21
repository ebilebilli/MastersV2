from rest_framework import serializers
from core.models.language_model import Language


class LanguageSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Language
        fields = '__all__'
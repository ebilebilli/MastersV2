from rest_framework import serializers

from reviews.models.rating_models import Rating


class RatingSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Rating
        fields = '__all__'


    
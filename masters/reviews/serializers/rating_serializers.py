from rest_framework import serializers

from reviews.models.rating_models import Rating, MasterRating


class RatingSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Rating
        fields = '__all__'


class MasterRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterRating
        fields = '__all__'

    
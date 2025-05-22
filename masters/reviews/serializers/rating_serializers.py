from rest_framework import serializers

from reviews.models.rating_models import Rating
# from reviews.models.rating_models import  MasterRating


class RatingSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Rating
        fields = '__all__'


# class MasterRatingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MasterRating
#         fields = '__all__'

    
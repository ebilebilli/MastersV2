from rest_framework import serializers

from masters.reviews.models.comment_models import Comment
from services.models.service_model import Service


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    
    class Meta:
        model = Comment
        fields = "__all__"
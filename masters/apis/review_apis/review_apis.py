from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404

from reviews.models.review_models import Review
from users.models.master_model import Master
from reviews.serializers.review_serializers import ReviewSerializer

__all__ = [
    'ReviewsForMasterAPIView',
    'CreateReviewAPIView',
    'UpdateReviewAPIView',
    'DeleteReviewAPIView',
    'FilterReviewAPIView'
]

class ReviewsForMasterAPIView(APIView):
    def get(self, request, master_id):
        try:
            master = Master.objects.get(is_active_on_main_page=True, id=master_id)
        except Master.DoesNotExist:
            
            return Response({'detail': 'Usta tapılmadı.'}, status=status.HTTP_404_NOT_FOUND)
        
        reviews = Review.objects.filter(master=master)
        
        serializer = ReviewSerializer(reviews, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CreateReviewAPIView(APIView):
    def post(self, request, master_id):
        try:
            master = Master.objects.get(is_active_on_main_page=True, id=master_id)
        except Master.DoesNotExist:
            return Response({'detail': 'Usta tapılmadı.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': 'Zəhmət olmasa bütün məcburi sahələri doldurun'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateReviewAPIView(APIView):
    def patch(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Zəhmət olmasa bütün məcburi sahələri doldurun'}, status=status.HTTP_400_BAD_REQUEST)
    
    
class DeleteReviewAPIView(APIView):
    def delete(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        review.delete()
        return Response({'message': 'Serhiniz ugurla silindi'}, status=status.HTTP_204_NO_CONTENT)
        
        
class FilterReviewAPIView(APIView):
    def get(self, request, master_id):
        master = get_object_or_404(Master, is_active_on_main_page=True, id=master_id)
        order = request.query_params.get('order', 'newest')
        if order == 'oldest':
            reviews = Review.objects.filter(master=master).order_by('created_at')  
        else:
            reviews = Review.objects.filter(master=master).order_by('-created_at')  

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
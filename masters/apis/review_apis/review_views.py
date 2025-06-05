from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import JSONParser, MultiPartParser
from django.db import transaction
from django.shortcuts import get_object_or_404

from reviews.models.review_models import Review
from masters.users.models.master_model import Master
from reviews.serializers.review_serializers import ReviewSerializer
from utils.paginations import CustomPagination
from utils.permissions import HeHasPermission

__all__ = [
    'ReviewsForMasterAPIView',
    'CreateReviewAPIView',
    'UpdateReviewAPIView',
    'DeleteReviewAPIView',
    'FilterReviewAPIView'
]

class ReviewsForMasterAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get(self, request, master_id):
        try:
            master = Master.objects.get(is_active_on_main_page=True, id=master_id)
        except Master.DoesNotExist:
            return Response({'detail': 'Usta tapılmadı.'}, status=status.HTTP_404_NOT_FOUND)
        
        pagination = self.pagination_class()
        reviews = Review.objects.filter(master=master)
        result_page = pagination.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)

    
class CreateReviewAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser]

    transaction.atomic
    def post(self, request, master_id):
        user = request.user
        try:
            master = Master.objects.get(is_active_on_main_page=True, id=master_id)
        except Master.DoesNotExist:
            return Response({'detail': 'Usta tapılmadı.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, master=master)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': 'Zəhmət olmasa bütün məcburi sahələri doldurun'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateReviewAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HeHasPermission]
    parser_classes = [JSONParser, MultiPartParser]

    @transaction.atomic
    def patch(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class DeleteReviewAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, HeHasPermission]

    @transaction.atomic
    def delete(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        review.delete()
        return Response({'message': 'Serhiniz ugurla silindi'}, status=status.HTTP_204_NO_CONTENT)
        
        
class FilterReviewAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get(self, request, master_id):
        pagination = self.pagination_class()
        master = get_object_or_404(Master, is_active_on_main_page=True, id=master_id)
        order = request.query_params.get('order', 'newest')
        if order == 'oldest':
            reviews = Review.objects.filter(master=master).order_by('created_at')  
        else:
            reviews = Review.objects.filter(master=master).order_by('-created_at') 

        result_page = pagination.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from django.db.models import Count

from users.models.master_model import Master
from users.serializers.master_serializer import MasterSerializer
from services.models.category_model import Category
from services.models.service_model import Service
from utils.paginations import CustomPagination


__all__ = [
    'MastersListAPIView',
    'MasterDetailAPIView',
    'MasterListForCategoryAPIView',
    'MasterListForServicesAPIView', 
    'FilteredMasterListAPIView'
]


class MastersListAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class =  CustomPagination

    def get(self, request):
        pagination = self.pagination_class()
        masters = Master.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        count_ratings=Count('reviews') 
    ).filter(is_active_on_main_page=True)
        
        if not masters.exists():
            return Response({
                'error': 'Hal-hazırda aktif bir usta yoxdur'
            }, status=status.HTTP_404_NOT_FOUND)
        result_page = pagination.paginate_queryset(masters, request)
        serializer = MasterSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)
    

class MasterDetailAPIView(APIView):
    def get(self, request, master_id):
        master = get_object_or_404(Master, id=master_id, is_active_on_main_page=True)
        serializer = MasterSerializer(master)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, master_id):
        user = request.user
        master = get_object_or_404(Master, id=master_id)
        serializer = MasterSerializer(master, partial=True)
        if master.id != user.id or not user.is_superuser:
            return Response({'error': 'Bunu etməyə icazəniz yoxdur'}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error':'error'}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, master_id):
        user = request.user
        master = get_object_or_404(Master, id=master_id) 
        if master.id != user.id or not user.is_superuser:
            return Response({'error': 'Bunu etməyə icazəniz yoxdur'}, status=status.HTTP_403_FORBIDDEN)
        
        if master:
            master.delete()
            return Response({'message': 'Hesab silindi'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Hesab tapılmadı'}, status=status.HTTP_404_NOT_FOUND)


class MasterListForCategoryAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class =  CustomPagination

    def get(self, request, category_id):
        pagination = self.pagination_class()
        category = get_object_or_404(Category, id=category_id)
        masters =  Master.objects.filter(profession_category=category, is_active_on_main_page=True)
        if not masters.exists():
            return Response({
                'error': 'Hal-hazırda bu kateqoriyaya uyğun aktif bir usta yoxdur'
            },status=status.HTTP_404_NOT_FOUND)
        result_page = pagination.paginate_queryset(masters, request)
        serializer = MasterSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)


class MasterListForServicesAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class =  CustomPagination

    def get(self, request, service_id):
        pagination = self.pagination_class()
        service = get_object_or_404(Service, id=service_id)
        masters =  Master.objects.filter(profession_service=service, is_active_on_main_page=True)
        if not masters.exists():
            return Response({
                'error': 'Hal-hazırda bu servisə uyğun aktif bir usta yoxdur'
            },status=status.HTTP_404_NOT_FOUND)
        result_page = pagination.paginate_queryset(masters, request)
        serializer = MasterSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)


class FilteredMasterListAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class =  CustomPagination

    def get(self, request):
        query = request.query_params.get('q')
        category_id = request.query_params.get('category_id')
        service_id = request.query_params.get('service_id')
        city_id = request.query_params.get('city_id')
        district_id = request.query_params.get('district_id')
        language_id = request.query_params.get('language_id')
        min_experience = request.query_params.get('min_experience')
        min_rating = request.query_params.get('min_rating')

        filters = Q(is_active_on_main_page=True)

        if query:
            filters &= Q(full_name__icontains=query) | Q(custom_profession__icontains=query)

        if category_id:
            filters &= Q(profession_category__id=category_id)

        if service_id:
            filters &= Q(profession_service__id=service_id)

        if city_id:
            filters &= Q(cities__id=city_id)

        if district_id:
            filters &= Q(districts__id=district_id)

        if language_id:
            filters &= Q(languages__id=language_id)

        if min_experience:
            try:
                min_experience = int(min_experience)
                filters &= Q(experience__gte=min_experience)
            except ValueError:
                pass

        masters = Master.objects.filter(filters).annotate(
            avg_rating=Avg('reviews__rating'),
            count_ratings=Count('reviews')
        ).distinct()

        if min_rating:
            try:
                min_rating = float(min_rating)
                masters = masters.filter(avg_rating__gte=min_rating)
            except ValueError:
                pass

        if not masters.exists():
            return Response(
                {'detail': 'Uyğun usta tapılmadı.'},
                status=status.HTTP_404_NOT_FOUND
            )
        pagination = self.pagination_class()
        result_page = pagination.paginate_queryset(masters, request)
        serializer = MasterSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)

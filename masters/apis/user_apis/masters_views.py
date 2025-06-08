from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Avg, Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.models.master_model import Master
from users.serializers.master_serializer import MasterSerializer
from utils.paginations import CustomPagination, PaginationForMainPage

__all__ = [
    'MastersListAPIView',
    'TopRatedMastersListAPIView',
    'MasterDetailAPIView'
]


class MastersListAPIView(APIView):
    """
    get:
    List all active masters with their average rating and number of reviews.
    """
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    http_method_names = ['get']

    @swagger_auto_schema(
        operation_description="Bütün aktiv ustaların orta reytinq və rəy sayı ilə səhifələnmiş siyahısını əldə edin.",
        responses={
            200: openapi.Response(
                description="Səhifələnmiş ustalar siyahısı",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Ümumi nəticə sayı"),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, description="Növbəti səhifənin URL-i", nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, description="Əvvəlki səhifənin URL-i", nullable=True),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=MasterSerializer,
                            description="Aktiv ustaların siyahısı"
                        )
                    }
                )
            ),
            404: openapi.Response(description="Hal-hazırda aktiv bir usta yoxdur.")
        }
    )
    def get(self, request):
        pagination = self.pagination_class()
        masters = Master.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            count_ratings=Count('reviews')
        ).filter(is_active_on_main_page=True)
        
        if not masters.exists():
            return Response({
                'error': 'Hal-hazırda aktiv bir usta yoxdur'
            }, status=status.HTTP_404_NOT_FOUND)
        result_page = pagination.paginate_queryset(masters, request)
        serializer = MasterSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)


class TopRatedMastersListAPIView(APIView):
    """
    get:
    Return a list of top-rated active masters sorted by rating, review count, and last login.
    """
    permission_classes = [AllowAny]
    pagination_class = PaginationForMainPage
    http_method_names = ['get']

    @swagger_auto_schema(
        operation_description="Ən yüksək reytinqli aktiv ustaların reytinq, rəy sayı və son girişə görə sıralanmış səhifələnmiş siyahısını əldə edin.",
        responses={
            200: openapi.Response(
                description="Səhifələnmiş ustalar siyahısı",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Ümumi nəticə sayı"),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, description="Növbəti səhifənin URL-i", nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, description="Əvvəlki səhifənin URL-i", nullable=True),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=MasterSerializer,
                            description="Ən yüksək reytinqli ustaların siyahısı"
                        )
                    }
                )
            ),
            404: openapi.Response(description="Hal-hazırda aktiv bir usta yoxdur.")
        }
    )
    def get(self, request):
        pagination = self.pagination_class()
        masters = Master.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            count_ratings=Count('reviews')
        ).filter(is_active_on_main_page=True).order_by('-avg_rating', '-count_ratings', '-last_login')
        
        if not masters.exists():
            return Response({
                'error': 'Hal-hazırda aktiv bir usta yoxdur'
            }, status=status.HTTP_404_NOT_FOUND)
        result_page = pagination.paginate_queryset(masters, request)
        serializer = MasterSerializer(result_page, many=True)
        paginated_response = pagination.get_paginated_response(serializer.data).data
        return Response(paginated_response, status=status.HTTP_200_OK)


class MasterDetailAPIView(APIView):
    """
    get:
    Retrieve a master's details by ID.

    patch:
    Update the master. Only the master themselves or a superuser can perform this.

    delete:
    Delete the master. Only the master themselves or a superuser can perform this.
    """
    http_method_names = ['get', 'patch', 'delete']
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Ustanın ID ilə ətraflı məlumatlarını əldə edin.",
        responses={
            200: MasterSerializer,
            404: openapi.Response(description="Usta tapılmadı.")
        },
        manual_parameters=[
            openapi.Parameter('master_id', openapi.IN_PATH, description="Ustanın ID-si", type=openapi.TYPE_INTEGER, required=True)
        ]
    )
    def get(self, request, master_id):
        master = get_object_or_404(Master, id=master_id, is_active_on_main_page=True)
        serializer = MasterSerializer(master)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Ustanın məlumatlarını yeniləyin (yalnız usta özü və ya superuser).",
        request_body=MasterSerializer,
        responses={
            200: MasterSerializer,
            400: openapi.Response(description="Daxil edilən məlumatlar səhvdir."),
            403: openapi.Response(description="Bunu etməyə icazəniz yoxdur."),
            404: openapi.Response(description="Usta tapılmadı.")
        },
        manual_parameters=[
            openapi.Parameter('master_id', openapi.IN_PATH, description="Ustanın ID-si", type=openapi.TYPE_INTEGER, required=True)
        ]
    )
    def patch(self, request, master_id):
        user = request.user
        master = get_object_or_404(Master, id=master_id)
        serializer = MasterSerializer(master, data=request.data, partial=True)
        if master.id != user.id and not user.is_superuser:
            return Response({'error': 'Bunu etməyə icazəniz yoxdur'}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Daxil edilən məlumatlar səhvdir'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Ustanı silin (yalnız usta özü və ya superuser).",
        responses={
            204: openapi.Response(description="Hesab uğurla silindi."),
            403: openapi.Response(description="Bunu etməyə icazəniz yoxdur."),
            404: openapi.Response(description="Usta tapılmadı.")
        },
        manual_parameters=[
            openapi.Parameter('master_id', openapi.IN_PATH, description="Ustanın ID-si", type=openapi.TYPE_INTEGER, required=True)
        ]
    )
    def delete(self, request, master_id):
        user = request.user
        master = get_object_or_404(Master, id=master_id)
        if master.id != user.id and not user.is_superuser:
            return Response({'error': 'Bunu etməyə icazəniz yoxdur'}, status=status.HTTP_403_FORBIDDEN)
        
        master.delete()
        return Response({'message': 'Hesab silindi'}, status=status.HTTP_204_NO_CONTENT)


# class FilteredMasterListAPIView(APIView):
#     permission_classes = [AllowAny]
#     pagination_class = CustomPagination
#     http_method_names = ['get']

#     def get(self, request):
#         query = request.query_params.get('q')
#         category_id = request.query_params.get('category_id')
#         service_id = request.query_params.get('service_id')
#         city_id = request.query_params.get('city_id')
#         district_id = request.query_params.get('district_id')
#         language_id = request.query_params.get('language_id')
#         min_experience = request.query_params.get('min_experience')
#         min_rating = request.query_params.get('min_rating')
#         sort_by = request.query_params.get('sort_by', 'newest')

#         filters = Q(is_active_on_main_page=True)

#         if query:
#             filters &= Q(full_name__icontains=query) | Q(custom_profession__icontains=query)
#         if category_id:
#             filters &= Q(profession_category__id=category_id)
#         if service_id:
#             filters &= Q(profession_service__id=service_id)
#         if city_id:
#             filters &= Q(cities__id=city_id)
#         if district_id:
#             filters &= Q(districts__id=district_id)
#         if language_id:
#             filters &= Q(languages__id=language_id)
#         if min_experience:
#             try:
#                 min_experience = int(min_experience)
#                 filters &= Q(experience__gte=min_experience)
#             except ValueError:
#                 pass

#         masters = Master.objects.filter(filters).annotate(
#             avg_rating=Avg('reviews__rating'),
#             count_ratings=Count('reviews')
#         ).distinct()

#         if min_rating:
#             try:
#                 min_rating = float(min_rating)
#                 masters = masters.filter(avg_rating__gte=min_rating)
#             except ValueError:
#                 pass

#         order_by = {
#             'newest': '-created_at',
#             'highest_rating': '-avg_rating',
#             'most_reviewed': '-count_ratings'
#         }.get(sort_by, '-created_at')
#         masters = masters.order_by(order_by)

#         if not masters.exists():
#             return Response(
#                 {'detail': 'Uyğun usta tapılmadı.'},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         pagination = self.pagination_class()
#         result_page = pagination.paginate_queryset(masters, request)
#         serializer = MasterSerializer(result_page, many=True, context={'request': request})
#         paginated_response = pagination.get_paginated_response(serializer.data).data
#         return Response(paginated_response, status=status.HTTP_200_OK)
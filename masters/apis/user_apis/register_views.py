from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.models import Master
from users.serializers.register_serializers import (
    PersonalInformationSerializer,
    ProfessionInformationSerializer,
    AdditionalInformationSerializer
)

portfolio_images = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Schema(type=openapi.TYPE_FILE, format='binary'),
    description="Portfolio şəkilləri (maksimum 10 ədəd, hər biri 5MB-dan böyük olmamalıdır)",
    max_items=10,
    nullable=True,
)


__all__ = [
    'RegisterPersonalAPIView',
    'RegisterProfessionAPIView',
    'RegisterAdditionalAPIView'
]


class RegisterPersonalAPIView(APIView):
    """
    Step 1 of registration:
    Create a new Master with personal information.
    """
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, MultiPartParser]
    http_method_names = ['post']
    
    @swagger_auto_schema(
        request_body=PersonalInformationSerializer,
        responses={
            201: 'Şəxsi məlumatlar uğurla saxlanıldı',
            400: 'Yanlış məlumat'
        }
    )

    @transaction.atomic
    def post(self, request):
        serializer = PersonalInformationSerializer(data=request.data)
        if serializer.is_valid():
            master = Master(
                phone_number=serializer.validated_data['phone_number'],
                full_name=serializer.validated_data['full_name'],
                birthday=serializer.validated_data['birthday'],
                gender=serializer.validated_data['gender'],
                is_active_on_main_page=False
            )
            master.set_password(serializer.validated_data['password'])
            master.save()
            refresh = RefreshToken.for_user(master)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return Response({
                'message': 'Şəxsi məlumatlar uğurla saxlanıldı',
                'phone_number': master.phone_number,
                'token': tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterProfessionAPIView(APIView):
    """
    Step 2 of registration:
    Update professional information for existing inactive Master.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [JSONParser, MultiPartParser]
    http_method_names = ['post']
    
    @swagger_auto_schema(
        request_body=ProfessionInformationSerializer,
        responses={
            200: 'Peşə məlumatları uğurla saxlanıldı',
            400: 'Yanlış məlumat',
            404: 'İstifadəçi tapılmadı'
        }
    )

    @transaction.atomic
    def post(self, request):
        user_id = request.user.id
        master = Master.objects.filter(id=user_id, is_active_on_main_page=False).first()
        if not master:
            return Response({
                'error': 'İstifadəçi tapılmadı və ya qeydiyyatın bu mərhələsinə uyğun deyil.'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfessionInformationSerializer(master, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Peşə məlumatları uğurla saxlanıldı',
                'phone_number': master.phone_number
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterAdditionalAPIView(APIView):
    """
    Step 3 of registration:
    Add additional info and activate the Master profile.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [JSONParser, MultiPartParser]
    http_method_names = ['post']
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['languages'],  # Əgər `languages` mütləqdirsə
        properties={
            'education': openapi.Schema(type=openapi.TYPE_STRING, description='Təhsil səviyyəsi'),
            'education_detail': openapi.Schema(type=openapi.TYPE_STRING, description='Təhsil ixtisası'),
            'languages': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_INTEGER),
                description='Dil ID-ləri',
            ),
            'profile_picture': openapi.Schema(type=openapi.TYPE_FILE, format='binary', description='Profil şəkli'),
            'facebook_url': openapi.Schema(type=openapi.TYPE_STRING, description='Facebook URL', nullable=True),
            'instagram_url': openapi.Schema(type=openapi.TYPE_STRING, description='Instagram URL', nullable=True),
            'tiktok_url': openapi.Schema(type=openapi.TYPE_STRING, description='TikTok URL', nullable=True),
            'linkedin_url': openapi.Schema(type=openapi.TYPE_STRING, description='LinkedIn URL', nullable=True),
            'youtube_url': openapi.Schema(type=openapi.TYPE_STRING, description='YouTube URL', nullable=True),
            'note': openapi.Schema(type=openapi.TYPE_STRING, description='Qeyd', nullable=True),
            'portfolio_images': portfolio_images,
        },
    ),
    responses={
        200: openapi.Response(description="Profiliniz uğurla yaradıldı!"),
        400: openapi.Response(description="Validation error"),
        403: openapi.Response(description="Yalnız ustalar üçün."),
        404: openapi.Response(description="İstifadəçi tapılmadı."),
    },
)

    @transaction.atomic
    def post(self, request):
        user_id = request.user.id
        master = Master.objects.filter(id=user_id, is_active_on_main_page=False).first()
        if not master:
            return Response({
                'error': 'İstifadəçi tapılmadı və ya qeydiyyatın bu mərhələsinə uyğun deyil.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AdditionalInformationSerializer(master, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            master.is_active_on_main_page = True
            master.save()

            return Response({'message': 'Profiliniz uğurla yaradıldı!'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
        operation_description="Qeydiyyatın 1-ci mərhələsi: Yeni usta üçün şəxsi məlumatları yaradın.",
        request_body=PersonalInformationSerializer,
        responses={
            201: openapi.Response(
                description="Şəxsi məlumatlar uğurla saxlanıldı.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Uğurlu əməliyyat mesajı"),
                        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description="Ustanın telefon nömrəsi"),
                        'token': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token"),
                                'access': openapi.Schema(type=openapi.TYPE_STRING, description="JWT access token")
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(description="Daxil edilən məlumatlar səhvdir.")
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
        operation_description="Qeydiyyatın 2-ci mərhələsi: Mövcud qeyri-aktiv usta üçün peşə məlumatlarını yeniləyin.",
        request_body=ProfessionInformationSerializer,
        responses={
            200: openapi.Response(
                description="Peşə məlumatları uğurla saxlanıldı.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Uğurlu əməliyyat mesajı"),
                        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description="Ustanın telefon nömrəsi")
                    }
                )
            ),
            400: openapi.Response(description="Daxil edilən məlumatlar səhvdir."),
            401: openapi.Response(description="İcazəsiz giriş."),
            404: openapi.Response(description="İstifadəçi tapılmadı və ya qeydiyyatın bu mərhələsinə uyğun deyil.")
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
        operation_description="Qeydiyyatın 3-cü mərhələsi: Əlavə məlumatlar əlavə edin və usta profilini aktivləşdirin.",
        request_body=AdditionalInformationSerializer,
        responses={
            200: openapi.Response(
                description="Profil uğurla yaradıldı.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Uğurlu əməliyyat mesajı")
                    }
                )
            ),
            400: openapi.Response(description="Daxil edilən məlumatlar səhvdir."),
            401: openapi.Response(description="İcazəsiz giriş."),
            404: openapi.Response(description="İstifadəçi tapılmadı və ya qeydiyyatın bu mərhələsinə uyğun deyil.")
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

        serializer = AdditionalInformationSerializer(master, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            master.is_active_on_main_page = True
            master.save()

            return Response({'message': 'Profiliniz uğurla yaradıldı!'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
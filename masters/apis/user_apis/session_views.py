from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.serializers.login_serializer import LoginSerializer
from users.serializers.password_serializers import PasswordResetConfirmSerializer, PasswordResetRequestSerializer
from users.models import Master
from users.tasks import send_otp

__all__ = [
    'LoginAPIView',
    'LogoutAPIView',
    'PasswordResetRequestAPIView',
    'PasswordResetConfirmAPIView'
]


class LoginAPIView(APIView):
    """
    API endpoint for user login using phone number and password.
    Returns access and refresh JWT tokens upon successful authentication.
    """
    permission_classes = [AllowAny]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="Telefon nömrəsi və parol ilə istifadəçi girişi. Uğurlu autentifikasiya zamanı JWT access və refresh tokenləri qaytarılır.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Uğurlu giriş",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Uğurlu giriş mesajı"),
                        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description="İstifadəçinin telefon nömrəsi"),
                        'tokens': openapi.Schema(
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
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response({
                'message': 'Uğurla daxil oldunuz!',
                'phone_number': user.phone_number,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """
    API endpoint for user logout.
    Blacklists the provided refresh token to invalidate it.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="İstifadəçi çıxışı üçün API endpointi. Təqdim olunan refresh tokeni qara siyahıya salınır.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token")
            },
            required=['refresh']
        ),
        responses={
            205: openapi.Response(description="Uğurla çıxış etdiniz."),
            400: openapi.Response(description="Refresh token daxil edilməyib və ya etibarsızdır."),
            401: openapi.Response(description="İcazəsiz giriş.")
        }
    )
    def post(self, request):
        """
        Handle POST request to blacklist the refresh token and log the user out.
        """
        refresh_token = request.data.get('refresh')

        try:
            if not refresh_token:
                return Response({'error': 'Refresh token daxil edilməyib.'}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Uğurla çıxış etdiniz!'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'error': 'Refresh token etibarsızdır.'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    """
    API endpoint to request a password reset OTP via phone number.
    Applies throttling to limit request rate.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="Telefon nömrəsi ilə parol sıfırlama OTP-si tələb etmək üçün API endpointi. Sorğu tezliyini məhdudlaşdırmaq üçün throttling tətbiq olunur.",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response(
                description="OTP uğurla göndərildi.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Uğurlu əməliyyat mesajı")
                    }
                )
            ),
            400: openapi.Response(description="Daxil edilən məlumatlar səhvdir."),
            500: openapi.Response(description="OTP göndərilə bilmədi.")
        }
    )
    @transaction.atomic
    def post(self, request):
        """
        Handle POST request to send an OTP for password reset.
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                send_otp(serializer.validated_data['phone_number'])
                serializer.save()
                return Response({
                    'message': 'OTP göndərildi.'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': f'OTP göndərilə bilmədi: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    """
    API endpoint to confirm password reset with OTP and new password.
    """
    permission_classes = [AllowAny]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="OTP və yeni parol ilə parol sıfırlamasını təsdiqləmək üçün API endpointi.",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response(
                description="Parol uğurla dəyişdirildi.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Uğurlu əməliyyat mesajı")
                    }
                )
            ),
            400: openapi.Response(description="Daxil edilən məlumatlar səhvdir."),
            500: openapi.Response(description="Parol dəyişdirilə bilmədi.")
        }
    )
    @transaction.atomic
    def post(self, request):
        """
        Handle POST request to reset the user's password using OTP.
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'message': 'Parol uğurla dəyişdirildi.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': f'Parol dəyişdirilə bilmədi: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
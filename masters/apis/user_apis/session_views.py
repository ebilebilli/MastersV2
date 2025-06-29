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
from users.tasks import send_otp_task

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
        request_body=LoginSerializer,
        responses={
            200: 'Uğurla daxil oldunuz!',
            400: 'Yanlış məlumat'
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
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            205: 'Uğurla çıxış etdiniz!',
            400: 'Etibarsız token və ya token daxil edilməyib'
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
    # throttle_classes = [AnonRateThrottle, UserRateThrottle]
    http_method_names = ['post']
    
    @swagger_auto_schema(
        request_body=PasswordResetRequestSerializer,
        responses={
            200: 'OTP göndərildi',
            400: 'Yanlış məlumat',
            500: 'OTP göndərilə bilmədi'
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
                send_otp_task.delay((serializer.validated_data['phone_number']))
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
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: 'Parol uğurla dəyişdirildi',
            400: 'Yanlış məlumat',
            500: 'Parol dəyişdirilə bilmədi'
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
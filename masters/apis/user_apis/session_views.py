from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction

from users.serializers.login_serializer import LoginSerializer

__all__ = [
    'LoginAPIView',
    'LogoutAPIView'
]

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        try:
            if not refresh_token:
                return Response({'error': 'Refresh token daxil edilməyib.'}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  
            return Response({  'message': 'Uğurla çıxış etdiniz!'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'error': 'Refresh token etibarsızdır.'}, status=status.HTTP_400_BAD_REQUEST)


        
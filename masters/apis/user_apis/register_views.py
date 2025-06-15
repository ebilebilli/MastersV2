from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.models import CustomerUser
from users.serializers.register_serializers import *

portfolio_images = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Schema(type=openapi.TYPE_FILE, format='binary'),
    description="Portfolio şəkilləri (maksimum 10 ədəd, hər biri 5MB-dan böyük olmamalıdır)",
    max_items=10,
    nullable=True,
)

__all__ = [
    'RegisterRoleSelectionAPIView',
    'RegisterPersonalAPIView',
    'RegisterProfessionAPIView',
    'RegisterAdditionalAPIView',
    'RegisterCustomerAPIView'
]

class RegisterRoleSelectionAPIView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ['post']

    @transaction.atomic
    def post(self, request):
        serializer = UserRoleSelectionSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomerUser(user_role = serializer.validated_data['user_role'])
            user.save()
            refresh = RefreshToken.for_user(user)

            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response({
                'message': 'Rol uğurla seçildi',
                'token': tokens
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterPersonalAPIView(APIView):
    """
    Step 1 of master registration:
    Create a new Master with personal information.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser]
    http_method_names = ['post']

    @transaction.atomic
    def post(self, request):
        if request.user.user_role != CustomerUser.MASTER: 
            return Response({
                'error': 'Bu qeydiyyat səhifəsi yalnız ustalar üçündür.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PersonalInformationSerializer(data=request.data)
        user_id = request.user.id
        master = CustomerUser.objects.filter(id=user_id, is_active_on_main_page=False).first()
        if serializer.is_valid():
            master = request.user 
            master.phone_number = serializer.validated_data['phone_number']
            master.full_name = serializer.validated_data['full_name']
            master.birthday = serializer.validated_data['birthday']
            master.gender = serializer.validated_data['gender']
            master.is_active_on_main_page = False

            master.set_password(serializer.validated_data['password'])
            master.save()
            
            return Response({
                'message': 'Şəxsi məlumatlar uğurla saxlanıldı',
                'phone_number': master.phone_number,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterProfessionAPIView(APIView):
    """
    Step 2 of master registration:
    Update professional information for existing inactive Master.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser]
    http_method_names = ['post']

    @transaction.atomic
    def post(self, request):
        if request.user.user_role != CustomerUser.MASTER: 
            return Response({
                'error': 'Bu qeydiyyat səhifəsi yalnız ustalar üçündür.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        master = CustomerUser.objects.filter(id=user_id, is_active_on_main_page=False).first()
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
    Step 3 of master registration:
    Add additional info and activate the Master profile.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
        if request.user.user_role != CustomerUser.MASTER:  
            return Response({
                'error': 'Bu qeydiyyat səhifəsi yalnız ustalar üçündür.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.user.id
        master = CustomerUser.objects.filter(id=user_id, is_active_on_main_page=False).first()
        if not master:
            return Response({
                'error': 'İstifadəçi tapılmadı və ya qeydiyyatın bu mərhələsinə uyğun deyil.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = AdditionalInformationSerializer(master, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            master.is_active_on_main_page = True
            master.is_master = True
            master.save()
            return Response({'message': 'Profiliniz uğurla yaradıldı!'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RegisterCustomerAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    @transaction.atomic
    def post(self, request):
        if request.user.user_role != CustomerUser.CUSTOMER: 
            return Response({'error': 'Bu qeydiyyat səhifəsi yalnız müştərilər üçündür.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            customer = request.user 
            customer.phone_number = serializer.validated_data['phone_number']
            customer.full_name = serializer.validated_data['full_name']
            customer.birthday = serializer.validated_data['birthday']
            customer.gender = serializer.validated_data['gender']
            customer.set_password(serializer.validated_data['password'])
            customer.is_active_on_main_page=True,
            customer.save()

            return Response({
                'message': 'Qeydiyyat uğurla tamamlandı',
                'phone_number': customer.phone_number,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

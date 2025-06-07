from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction

from users.models import Master
from users.serializers.register_serializers import(
    UserRoleSelectionSerializer,
    PersonalInformationSerializer,
    ProfessionInformationSerializer,
    AdditionalInformationSerializer
)


__all__ = [
    'RegisterPersonalAPIView',
    'RegisterProfessionAPIView',
    'RegisterAdditionalAPIView',
    'RegisterRoleSelectionAPIView'
]

class RegisterRoleSelectionAPIView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ['post']

    @transaction.atomic
    def post(self, request):
        serializer = UserRoleSelectionSerializer(data=request.data)
        if serializer.is_valid():
            user = Master(user_role = serializer.validated_data['user_role'])
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
        if request.user.user_role != Master.MASTER: 
            return Response({
                'error': 'Bu qeydiyyat səhifəsi yalnız ustalar üçündür.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PersonalInformationSerializer(data=request.data)
        user_id = request.user.id
        master = Master.objects.filter(id=user_id, is_active_on_main_page=False).first()
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
        if request.user.user_role != Master.MASTER: 
            return Response({
                'error': 'Bu qeydiyyat səhifəsi yalnız ustalar üçündür.'
            }, status=status.HTTP_403_FORBIDDEN)
        
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
    Step 3 of master registration:
    Add additional info and activate the Master profile.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser]
    http_method_names = ['post']

    @transaction.atomic
    def post(self, request):
        if request.user.user_role != Master.MASTER:  
            return Response({
                'error': 'Bu qeydiyyat səhifəsi yalnız ustalar üçündür.'
            }, status=status.HTTP_403_FORBIDDEN)
        
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
            master.is_master = True
            master.save()

            return Response({'message': 'Profiliniz uğurla yaradıldı!'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    

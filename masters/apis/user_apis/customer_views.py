from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.db import transaction

from users.models import Master
from users.serializers.register_serializers import (
    
    PersonalInformationSerializer,
    ProfessionInformationSerializer,
    AdditionalInformationSerializer
)



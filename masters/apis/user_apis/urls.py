from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from apis.user_apis.session_views import *
from apis.user_apis.register_views import (
    RegisterPersonalAPIView,
    ProfessionRegisterAPIView,
    RegisterAdditionaAPIView,
)


app_name = 'user_apis'

urlpatterns = [   
                
    #Register endpoints
    path(
        'register/personal/',
        RegisterPersonalAPIView.as_view(),
        name='register-personal'
    ),

    path(
        'register/profession/',
        ProfessionRegisterAPIView.as_view(),
        name='register-profession'
    ),
    
    path(
        'register/additional/',
        RegisterAdditionaAPIView.as_view(),
        name='register-additional'
    ),
    
    #Session endpoints
    path(
        "login/",
        LoginAPIView.as_view(),
        name='login'
    ),
    
    path(
        'logout/',
        LogoutAPIView.as_view(),
        name='logout'
    ),

    #Jwt endpoints
    path(
        'api/token/', 
        jwt_views.TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    
    path(
        'api/token/refresh/',
        jwt_views.TokenRefreshView.as_view(),
        name='token_refresh'
    ),
]
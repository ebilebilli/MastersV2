from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from apis.user_apis.session_views import *
from apis.user_apis.masters_views import *
from apis.user_apis.register_views import *


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
        RegisterProfessionAPIView.as_view(),
        name='register-profession'
    ),
    
    path(
        'register/additional/',
        RegisterAdditionalAPIView.as_view(),
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
    
    path(
        'password/reset/request/',
        PasswordResetRequestAPIView.as_view(),
        name='password-reset-request'  
    ),
    
    path(
        'password/reset/confirm/',
        PasswordResetConfirmAPIView.as_view(),
        name='password-reset-confirm'
    ),

    # Master endpoints
    path(
        'masters/', 
        MastersListAPIView.as_view(), 
        name='masters-list'
    ),

    path(
        'masters/<int:master_id>/', 
        MasterDetailAPIView.as_view(),
        name='master-detail'
    ),

    path(
        'masters/category/<int:category_id>/', 
        MasterListForCategoryAPIView.as_view(), 
        name='masters-by-category'
    ),

    path(
        'masters/service/<int:service_id>/', 
        MasterListForServicesAPIView.as_view(), 
        name='masters-by-service'
    ),

    path(
        'masters/filter/', 
        FilteredMasterListAPIView.as_view(), 
        name='masters-filter'
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
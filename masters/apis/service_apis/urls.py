from django.urls import path

from apis.service_apis.category_views import *
from apis.service_apis.service_views import *


app_name = 'service_apis'

urlpatterns = [
    #Category endpoints
    path(
        'categories/',
        CategoryListAPIView.as_view(),
        name='categories'
    ),
    path(
        'masters/category/<int:category_id>/', 
        MasterListForCategoryAPIView.as_view(), 
        name='masters-by-category'
    ),

    #Service endpoints
     path(
        'services/',
        ServiceListAPIView.as_view(),
        name='services '
    ),
    path(
        'category/<int:category_id>/services/',
        ServicesForCategoryAPIView.as_view(),
        name='services-for-category'
    ),
    path(
        'masters/service/<int:service_id>/', 
        MasterListForServicesAPIView.as_view(), 
        name='masters-by-service'
    ),
]

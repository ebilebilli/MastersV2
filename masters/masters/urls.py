from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from masters.settings import MEDIA_URL, MEDIA_ROOT

schema_view = get_schema_view(
    openapi.Info(
        title="Masters project APIs",
        default_version='v1',
        description="API documentation for project",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apis.core_apis.urls', namespace='core_apis')),
    path('api/v1/', include('apis.service_apis.urls', namespace='service_apis')),
    path('api/v1/', include('apis.review_apis.urls', namespace='review_apis')),
    path('api/v1/', include('apis.user_apis.urls', namespace='user_apis')),
    path('api/v1/', include('apis.search_apis.urls', namespace='search_apis')),

    # Swagger & Redoc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
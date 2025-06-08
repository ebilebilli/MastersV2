from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.permissions import AllowAny
from utils.paginations import CustomPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response

__all__ = [
    'SearchAPIView'
]

es_client = Elasticsearch(hosts=[settings.ELASTICSEARCH_HOST])

search_param = openapi.Parameter('search', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING)
profession_category_id_param = openapi.Parameter('profession_category_id', openapi.IN_QUERY, description="Filter by profession category ID", type=openapi.TYPE_INTEGER)
profession_service_id_param = openapi.Parameter('profession_service_id', openapi.IN_QUERY, description="Filter by profession service ID", type=openapi.TYPE_INTEGER)
city_id_param = openapi.Parameter('city_id', openapi.IN_QUERY, description="Filter by city ID", type=openapi.TYPE_INTEGER)
district_id_param = openapi.Parameter('district_id', openapi.IN_QUERY, description="Filter by district ID", type=openapi.TYPE_INTEGER)
experience_param = openapi.Parameter('experience', openapi.IN_QUERY, description="Filter by exact years of experience", type=openapi.TYPE_INTEGER)
ordering_param = openapi.Parameter('ordering', openapi.IN_QUERY, description="Field to order by, e.g., 'experience', 'full_name.keyword'", type=openapi.TYPE_STRING)
page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
page_size_param = openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size (max 100)", type=openapi.TYPE_INTEGER)
class SearchAPIView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ['get']

    @swagger_auto_schema(
        manual_parameters=[
            search_param,
            profession_category_id_param,
            profession_service_id_param,
            city_id_param,
            district_id_param,
            experience_param,
            ordering_param,
            page_param,
            page_size_param
        ],
        operation_summary="Search and filter masters",
        operation_description="Search with filters and keywords"
    )
    def get(self, request):
        profession_category_id = request.GET.get('profession_category_id')
        profession_service_id = request.GET.get('profession_service_id')
        city_id = request.GET.get('city_id')
        district_id = request.GET.get('district_id')
        experience = request.GET.get('experience')
        search_query = request.GET.get('search')
        ordering = request.GET.get('ordering')

        must_filters = []

        if profession_category_id:
            must_filters.append({
                "term": {"profession_category.id": int(profession_category_id)}
            })

        if profession_service_id:
            must_filters.append({
                "term": {"profession_service.id": int(profession_service_id)}
            })

        if city_id:
            must_filters.append({
                "nested": {
                    "path": "cities",
                    "query": {
                        "term": {"cities.id": int(city_id)}
                    }
                }
            })

        if district_id:
            must_filters.append({
                "nested": {
                    "path": "districts",
                    "query": {
                        "term": {"districts.id": int(district_id)}
                    }
                }
            })

        if experience:
            try:
                must_filters.append({
                    "term": {"experience": int(experience)}
                })
            except ValueError:
                pass

        # Əsas query qurulması
        bool_query = {
            "must": must_filters  # İlk növbədə filter kimi istifadə olunan termlər must-dadır
        }

        if search_query:
            # search_query varsa, onu must-ə əlavə et
            bool_query["must"].append({
                "multi_match": {
                    "query": search_query,
                    "fields": [
                        "full_name",
                        "custom_profession",
                        "profession_category.name",
                        "profession_service.name"
                    ]
                }
            })

            # cities və districts üçün nested match-lər də əlavə etmək istəsən, onları da must-ə əlavə et
            bool_query["must"].extend([
                {
                    "nested": {
                        "path": "cities",
                        "query": {
                            "match": {"cities.name": search_query}
                        }
                    }
                },
                {
                    "nested": {
                        "path": "districts",
                        "query": {
                            "match": {"districts.name": search_query}
                        }
                    }
                }
            ])

        query_body = {
            "query": {
                "bool": bool_query
            }
        }

        if ordering:
            query_body["sort"] = [ordering]

        try:
            page = int(request.GET.get('page', 1))
            page_size = min(
                int(request.GET.get('page_size', CustomPagination.page_size)),
                CustomPagination.max_page_size
            )
        except ValueError:
            page = 1
            page_size = CustomPagination.page_size

        from_ = (page - 1) * page_size

        response = es_client.search(
            index="masters",
            body=query_body,
            size=page_size,
            from_=from_
        )

        results = [hit["_source"] for hit in response["hits"]["hits"]]
        pagination = CustomPagination()
        result_page = pagination.paginate_queryset(results, request, view=self)
        return pagination.get_paginated_response(result_page)

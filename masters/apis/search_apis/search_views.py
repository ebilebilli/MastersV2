from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.permissions import AllowAny
from utils.paginations import CustomPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

__all__ = [
    'SearchAPIView'
]

es_client = Elasticsearch(hosts=[settings.ELASTICSEARCH_HOST])

class SearchAPIView(APIView):
    """
    get:
    Search and filter masters using Elasticsearch.

    This endpoint allows users to search for masters using multiple filter parameters.
    Results are fetched from the Elasticsearch index named "masters" and paginated.

    Query Parameters:
    - `search` (str, optional): A text-based query for full name, profession, city, etc.
    - `profession_category_id` (int, optional): Filter by profession category ID.
    - `profession_service_id` (int, optional): Filter by profession service ID.
    - `city_id` (int, optional): Filter by city ID (nested in `cities` field).
    - `district_id` (int, optional): Filter by district ID (nested in `districts` field).
    - `experience` (int, optional): Filter by exact years of experience.
    - `ordering` (str, optional): Field to sort by (e.g. `"experience"`, `"full_name.keyword"`).
    - `page` (int, optional): Page number for pagination.
    - `page_size` (int, optional): Number of results per page (default is 10, max 100).

    Response:
    A paginated list of matched masters with relevant details.
    """
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    http_method_names = ['get']

    @swagger_auto_schema(
        operation_description="Elasticsearch istifadə edərək ustaları axtarmaq və filtrləmək. Nəticələr səhifələnmiş şəkildə qaytarılır.",
        responses={
            200: openapi.Response(
                description="Uğurlu cavab, səhifələnmiş ustalar siyahısı.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Ümumi nəticə sayı"),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, description="Növbəti səhifənin URL-i", nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, description="Əvvəlki səhifənin URL-i", nullable=True),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                description="Usta məlumatları",
                                additional_properties=True
                            ),
                            description="Axtarış nəticələri"
                        )
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Tam ad, peşə, şəhər və s. üçün axtarış sorğusu", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('profession_category_id', openapi.IN_QUERY, description="Peşə kateqoriyasının ID-si", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('profession_service_id', openapi.IN_QUERY, description="Peşə xidmətinin ID-si", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('city_id', openapi.IN_QUERY, description="Şəhərin ID-si (cities sahəsində nested)", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('district_id', openapi.IN_QUERY, description="Rayonun ID-si (districts sahəsində nested)", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('experience', openapi.IN_QUERY, description="Təcrübə illəri (dəqiq uyğunluq)", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Sıralama sahəsi (məsələn, 'experience', 'full_name.keyword')", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('page', openapi.IN_QUERY, description="Səhifə nömrəsi", type=openapi.TYPE_INTEGER, required=False, default=1),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Səhifə başına nəticə sayı (defolt 10, maksimum 100)", type=openapi.TYPE_INTEGER, required=False)
        ]
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
                exp_int = int(experience)
                must_filters.append({
                    "term": {"experience": exp_int}
                })
            except ValueError:
                pass

        query_body = {
            "query": {
                "bool": {
                    "filter": must_filters
                }
            }
        }

        if search_query:
            query_body["query"] = {
                "bool": {
                    "filter": must_filters,
                    "must": {
                        "multi_match": {
                            "query": search_query,
                            "fields": [
                                "full_name",
                                "custom_profession",
                                "profession_category.name",
                                "profession_service.name",
                                "cities.name",
                                "districts.name"
                            ]
                        }
                    }
                }
            }

        if ordering:
            query_body["sort"] = [ordering]

        page = int(request.GET.get('page', 1))
        page_size = self.pagination_class.page_size
        page_size = min(
            int(request.GET.get('page_size', page_size)),
            self.pagination_class.max_page_size
        )
        from_ = (page - 1) * page_size

        response = es_client.search(
            index="masters",
            body=query_body,
            size=page_size,
            from_=from_
        )

        results = [hit["_source"] for hit in response["hits"]["hits"]]
        pagination = self.pagination_class()
        result_page = pagination.paginate_queryset(results, request, view=self)
        return pagination.get_paginated_response(result_page)
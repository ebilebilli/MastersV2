from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from django.conf import settings

from rest_framework.permissions import AllowAny
from utils.paginations import CustomPagination

__all__ = [
    'SearchAPIView'
]

es_client = Elasticsearch(hosts=[settings.ELASTICSEARCH_HOST])

class SearchAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    http_method_names = ['get']


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
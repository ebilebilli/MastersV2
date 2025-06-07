from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    General purpose pagination with default page size 10.
    Allows client to override page size up to max_page_size.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PaginationForMainPage(PageNumberPagination):
    """
    Pagination for the main page with default page size 8.
    """
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100


class PaginationForReviewPage(PageNumberPagination):
    """
    Pagination for the review page with default page size 5.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

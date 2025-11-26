from rest_framework.pagination import PageNumberPagination


class UsuarioPagination(PageNumberPagination):
    """Paginación personalizada para usuarios"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
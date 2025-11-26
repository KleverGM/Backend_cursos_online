from rest_framework.pagination import PageNumberPagination


class InscripcionPagination(PageNumberPagination):
    """Paginación personalizada para inscripciones"""
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 50
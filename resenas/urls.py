from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResenaViewSet

# Configurar el router con acciones explícitas
resena_list = ResenaViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

resena_detail = ResenaViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

resena_marcar_util = ResenaViewSet.as_view({
    'post': 'marcar_util'
})

resena_responder = ResenaViewSet.as_view({
    'post': 'responder'
})

resena_mis_resenas = ResenaViewSet.as_view({
    'get': 'mis_resenas'
})

resena_estadisticas = ResenaViewSet.as_view({
    'get': 'estadisticas_curso'
})

urlpatterns = [
    path('mis_resenas/', resena_mis_resenas, name='resena-mis-resenas'),
    path('estadisticas_curso/', resena_estadisticas, name='resena-estadisticas'),
    path('', resena_list, name='resena-list'),
    path('<str:pk>/', resena_detail, name='resena-detail'),
    path('<str:pk>/marcar_util/', resena_marcar_util, name='resena-marcar-util'),
    path('<str:pk>/responder/', resena_responder, name='resena-responder'),
]
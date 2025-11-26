from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear el router para las API de avisos
router = DefaultRouter()
router.register('avisos', views.AvisoViewSet, basename='aviso')

urlpatterns = [
    # Rutas de la API de avisos
    path('', include(router.urls)),
]
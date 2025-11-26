from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear el router para las API de modulos
router = DefaultRouter()
router.register('modulos', views.ModuloViewSet)

urlpatterns = [
    # Rutas de la API de módulos
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear el router para las API de secciones
router = DefaultRouter()
router.register('secciones', views.SeccionViewSet)
router.register('progreso-secciones', views.ProgresoSeccionViewSet, basename='progresoseccion')

urlpatterns = [
    # Rutas de la API de secciones
    path('', include(router.urls)),
]
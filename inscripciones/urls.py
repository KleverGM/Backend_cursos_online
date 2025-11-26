from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear el router para las API de inscripciones
router = DefaultRouter()
router.register('inscripciones', views.InscripcionViewSet, basename='inscripcion')

urlpatterns = [
    # Rutas de la API de inscripciones
    path('', include(router.urls)),
]
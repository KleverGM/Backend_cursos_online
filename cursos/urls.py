from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear el router para las API de cursos
router = DefaultRouter()
router.register('cursos', views.CursoViewSet)

urlpatterns = [
    # Rutas de la API de cursos
    path('', include(router.urls)),
]
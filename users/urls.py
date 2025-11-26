from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

# Crear el router para las API de usuarios
router = DefaultRouter()
router.register('users', views.UsuarioViewSet, basename='users')

urlpatterns = [
    # API de autenticación JWT
    path('users/login/', views.login_view, name='login'),
    path('users/register/', views.register_view, name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Rutas de la API de usuarios
    path('', include(router.urls)),
]
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from ..models import Modulo
from ..serializers import ModuloSerializer, ModuloDetalladoSerializer
from ..permissions import IsOwnerOrAdmin


class CustomPermission:
    """Permisos personalizados para diferentes tipos de usuarios"""
    
    @staticmethod
    def es_instructor_o_admin(user):
        return user.perfil in ['instructor', 'administrador']
    
    @staticmethod
    def es_propietario_o_admin(user, obj):
        if hasattr(obj, 'instructor'):
            return obj.instructor == user or user.perfil == 'administrador'
        elif hasattr(obj, 'usuario'):
            return obj.usuario == user or user.perfil == 'administrador'
        return user.perfil == 'administrador'


class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['curso']
    ordering_fields = ['orden']
    ordering = ['curso', 'orden']
    
    def get_permissions(self):
        """Permitir acceso público para ver módulos (son solo estructura/índice)"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ModuloDetalladoSerializer
        return ModuloSerializer
    
    def perform_create(self, serializer):
        # Solo el instructor del curso o admin pueden crear módulos
        curso = serializer.validated_data['curso']
        if not CustomPermission.es_propietario_o_admin(self.request.user, curso):
            raise permissions.PermissionDenied("No tienes permisos para crear módulos en este curso")
        serializer.save()
    
    def perform_update(self, serializer):
        modulo = self.get_object()
        if not CustomPermission.es_propietario_o_admin(self.request.user, modulo.curso):
            raise permissions.PermissionDenied("No tienes permisos para editar este módulo")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Solo el instructor del curso o admin pueden eliminar módulos
        if not CustomPermission.es_propietario_o_admin(self.request.user, instance.curso):
            raise permissions.PermissionDenied("No tienes permisos para eliminar este módulo")
        
        # Eliminar explícitamente las secciones primero (aunque CASCADE debería hacerlo)
        instance.secciones.all().delete()
        instance.delete()
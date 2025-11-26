from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from ..models import Aviso
from ..serializers import AvisoSerializer
from ..permissions import IsOwnerOrAdmin


class AvisoViewSet(viewsets.ModelViewSet):
    queryset = Aviso.objects.all()
    serializer_class = AvisoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['tipo', 'leido']
    ordering_fields = ['fecha_creacion']
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        # Los usuarios normales solo ven sus propios avisos
        if self.request.user.perfil == 'administrador':
            return Aviso.objects.all()
        return Aviso.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
    
    def perform_update(self, serializer):
        # Solo el propietario o admin pueden actualizar
        if (self.request.user.perfil != 'administrador' and 
            self.get_object().usuario != self.request.user):
            raise permissions.PermissionDenied("No tienes permisos para actualizar este aviso")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Solo el propietario o admin pueden eliminar
        if (self.request.user.perfil != 'administrador' and 
            instance.usuario != self.request.user):
            raise permissions.PermissionDenied("No tienes permisos para eliminar este aviso")
        instance.delete()
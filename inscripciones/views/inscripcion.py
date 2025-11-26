from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from ..models import Inscripcion
from ..serializers import InscripcionSerializer, InscripcionDetalladaSerializer
from ..permissions import IsOwnerOrAdmin


class InscripcionViewSet(viewsets.ModelViewSet):
    queryset = Inscripcion.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['completado', 'curso']
    ordering_fields = ['fecha_inscripcion', 'progreso']
    ordering = ['-fecha_inscripcion']
    
    def get_queryset(self):
        # Los usuarios normales solo ven sus propias inscripciones
        if self.request.user.perfil == 'administrador':
            return Inscripcion.objects.all()
        return Inscripcion.objects.filter(usuario=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InscripcionDetalladaSerializer
        return InscripcionSerializer
    
    def perform_create(self, serializer):
        # Solo estudiantes pueden inscribirse
        if self.request.user.perfil != 'estudiante':
            raise permissions.PermissionDenied("Solo estudiantes pueden inscribirse en cursos")
        serializer.save(usuario=self.request.user)
    
    def perform_update(self, serializer):
        # Solo administradores pueden actualizar inscripciones
        if self.request.user.perfil != 'administrador':
            raise permissions.PermissionDenied("No tienes permisos para actualizar esta inscripción")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Solo el propietario o admin pueden eliminar inscripciones
        if (self.request.user.perfil != 'administrador' and 
            instance.usuario != self.request.user):
            raise permissions.PermissionDenied("No tienes permisos para eliminar esta inscripción")
        instance.delete()
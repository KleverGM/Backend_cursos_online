from rest_framework import viewsets, permissions, exceptions
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
        # Administradores ven todas las inscripciones
        if self.request.user.perfil == 'administrador':
            return Inscripcion.objects.all()
        # Instructores ven inscripciones de sus cursos
        elif self.request.user.perfil == 'instructor':
            from cursos.models import Curso
            mis_cursos = Curso.objects.filter(instructor=self.request.user)
            return Inscripcion.objects.filter(curso__in=mis_cursos)
        # Estudiantes ven solo sus propias inscripciones
        return Inscripcion.objects.filter(usuario=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InscripcionDetalladaSerializer
        return InscripcionSerializer
    
    def perform_create(self, serializer):
        # Los estudiantes se inscriben a sí mismos
        # Los administradores pueden inscribir a cualquier estudiante
        
        if self.request.user.perfil == 'estudiante':
            # Estudiante se inscribe a sí mismo
            serializer.save(usuario=self.request.user)
        elif self.request.user.perfil == 'administrador':
            # Administrador puede inscribir al estudiante especificado en el request
            # Si no se especifica usuario_id, se requiere en el body
            if not serializer.validated_data.get('usuario'):
                # Si el admin no especifica, inscribe al usuario del request
                serializer.save()
            else:
                serializer.save()
        else:
            raise exceptions.PermissionDenied("Solo estudiantes y administradores pueden crear inscripciones")
    
    def perform_update(self, serializer):
        instance = self.get_object()
        
        # Administradores pueden actualizar cualquier campo de cualquier inscripción
        if self.request.user.perfil == 'administrador':
            serializer.save()
        # Estudiantes solo pueden actualizar progreso de sus propias inscripciones
        elif self.request.user.perfil == 'estudiante' and instance.usuario == self.request.user:
            # Solo permitir actualización de progreso y completado
            campos_permitidos = {'progreso', 'completado'}
            campos_enviados = set(serializer.validated_data.keys())
            
            # Verificar si hay campos no permitidos
            campos_no_permitidos = campos_enviados - campos_permitidos
            if campos_no_permitidos:
                raise exceptions.PermissionDenied(
                    f"Solo puedes actualizar los campos: progreso, completado"
                )
            serializer.save()
        # Instructores no pueden actualizar inscripciones
        else:
            raise exceptions.PermissionDenied("No tienes permisos para actualizar esta inscripción")
    
    def perform_destroy(self, instance):
        # Solo el propietario o admin pueden eliminar inscripciones
        if (self.request.user.perfil != 'administrador' and 
            instance.usuario != self.request.user):
            raise permissions.PermissionDenied("No tienes permisos para eliminar esta inscripción")
        instance.delete()
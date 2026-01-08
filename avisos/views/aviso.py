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
        if self.request.user.perfil == 'administrador':
            return Aviso.objects.all()
        return Aviso.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        usuario_id = serializer.validated_data.pop('usuario_id', None)
        
        # Admin puede crear avisos para cualquier usuario
        if self.request.user.perfil == 'administrador':
            if usuario_id:
                try:
                    usuario = User.objects.get(id=usuario_id)
                    serializer.save(usuario=usuario)
                except User.DoesNotExist:
                    raise permissions.PermissionDenied("El usuario especificado no existe")
            else:
                raise permissions.PermissionDenied("Debes especificar un usuario_id")
        
        # Instructores pueden crear avisos para estudiantes de sus cursos
        elif self.request.user.perfil == 'instructor':
            if usuario_id:
                try:
                    usuario = User.objects.get(id=usuario_id)
                    # Verificar que el usuario esté inscrito en algún curso del instructor
                    from inscripciones.models import Inscripcion
                    from cursos.models import Curso
                    
                    cursos_instructor = Curso.objects.filter(instructor=self.request.user)
                    if not Inscripcion.objects.filter(usuario=usuario, curso__in=cursos_instructor).exists():
                        raise permissions.PermissionDenied(
                            "Solo puedes enviar avisos a estudiantes inscritos en tus cursos"
                        )
                    serializer.save(usuario=usuario)
                except User.DoesNotExist:
                    raise permissions.PermissionDenied("El usuario especificado no existe")
            else:
                raise permissions.PermissionDenied("Debes especificar un usuario_id")
        
        # Estudiantes no pueden crear avisos
        else:
            raise permissions.PermissionDenied("No tienes permisos para crear avisos")
    
    def perform_update(self, serializer):
        instance = self.get_object()
        
        # Admin puede actualizar cualquier aviso
        if self.request.user.perfil == 'administrador':
            serializer.save()
        # Usuarios solo pueden actualizar sus propios avisos (marcar como leído)
        elif instance.usuario == self.request.user:
            # Solo permitir actualizar leido y comentario
            campos_permitidos = {'leido', 'comentario'}
            campos_enviados = set(serializer.validated_data.keys())
            
            campos_no_permitidos = campos_enviados - campos_permitidos
            if campos_no_permitidos:
                raise permissions.PermissionDenied(
                    f"Solo puedes actualizar los campos: leido, comentario"
                )
            serializer.save()
        else:
            raise permissions.PermissionDenied("No tienes permisos para actualizar este aviso")
    
    def perform_destroy(self, instance):
        # Solo admin e instructores pueden eliminar avisos
        if self.request.user.perfil == 'administrador':
            instance.delete()
        elif self.request.user.perfil == 'instructor':
            # Instructor solo puede eliminar avisos que él creó para sus estudiantes
            from inscripciones.models import Inscripcion
            from cursos.models import Curso
            
            cursos_instructor = Curso.objects.filter(instructor=self.request.user)
            if Inscripcion.objects.filter(usuario=instance.usuario, curso__in=cursos_instructor).exists():
                instance.delete()
            else:
                raise permissions.PermissionDenied("No tienes permisos para eliminar este aviso")
        else:
            raise permissions.PermissionDenied("No tienes permisos para eliminar avisos")
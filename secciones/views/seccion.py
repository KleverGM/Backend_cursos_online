from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from ..models import Seccion, ProgresoSeccion
from ..serializers import SeccionSerializer, SeccionDetalladaSerializer, ProgresoSeccionSerializer
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


class SeccionViewSet(viewsets.ModelViewSet):
    queryset = Seccion.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['modulo', 'modulo__curso']
    ordering_fields = ['orden']
    ordering = ['modulo', 'orden']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SeccionDetalladaSerializer
        return SeccionSerializer
    
    def perform_create(self, serializer):
        # Solo el instructor del curso o admin pueden crear secciones
        modulo = serializer.validated_data['modulo']
        if not CustomPermission.es_propietario_o_admin(self.request.user, modulo.curso):
            raise permissions.PermissionDenied("No tienes permisos para crear secciones en este curso")
        serializer.save()
    
    def perform_update(self, serializer):
        seccion = self.get_object()
        if not CustomPermission.es_propietario_o_admin(self.request.user, seccion.modulo.curso):
            raise permissions.PermissionDenied("No tienes permisos para editar esta sección")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Solo el instructor del curso o admin pueden eliminar secciones
        if not CustomPermission.es_propietario_o_admin(self.request.user, instance.modulo.curso):
            raise permissions.PermissionDenied("No tienes permisos para eliminar esta sección")
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def marcar_completado(self, request, pk=None):
        """Marcar una sección como completada por el usuario"""
        seccion = self.get_object()
        progreso, created = ProgresoSeccion.objects.get_or_create(
            usuario=request.user,
            seccion=seccion,
            defaults={'completado': True, 'tiempo_visto': seccion.duracion_minutos * 60}
        )
        
        if not created:
            progreso.completado = True
            progreso.save()
        
        # Actualizar progreso del curso
        self._actualizar_progreso_curso(request.user, seccion.modulo.curso)
        
        return Response({'message': 'Sección marcada como completada'})
    
    def _actualizar_progreso_curso(self, usuario, curso):
        """Actualizar el progreso general del curso"""
        from inscripciones.models import Inscripcion
        
        try:
            inscripcion = Inscripcion.objects.get(usuario=usuario, curso=curso)
            total_secciones = Seccion.objects.filter(modulo__curso=curso).count()
            secciones_completadas = ProgresoSeccion.objects.filter(
                usuario=usuario,
                seccion__modulo__curso=curso,
                completado=True
            ).count()
            
            if total_secciones > 0:
                progreso = (secciones_completadas / total_secciones) * 100
                inscripcion.progreso = progreso
                inscripcion.completado = progreso >= 100
                inscripcion.save()
        except Inscripcion.DoesNotExist:
            pass


class ProgresoSeccionViewSet(viewsets.ModelViewSet):
    queryset = ProgresoSeccion.objects.all()
    serializer_class = ProgresoSeccionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['completado', 'seccion__modulo__curso']
    
    def get_queryset(self):
        # Solo mostrar el progreso del usuario autenticado
        return ProgresoSeccion.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
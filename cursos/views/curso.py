from django.contrib.auth import get_user_model
from django.db.models import Q, Sum, Avg, Count
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..models import Curso
from ..serializers import CursoSerializer, CursoDetalladoSerializer
from ..permissions import IsOwnerOrAdmin, IsInstructorOrAdmin

User = get_user_model()


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


class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.filter(activo=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria', 'nivel', 'instructor']
    search_fields = ['titulo', 'descripcion']
    ordering_fields = ['fecha_creacion', 'titulo', 'precio']
    ordering = ['-fecha_creacion']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CursoDetalladoSerializer
        return CursoSerializer
    
    def perform_create(self, serializer):
        # Solo instructores y admins pueden crear cursos
        if not CustomPermission.es_instructor_o_admin(self.request.user):
            raise permissions.PermissionDenied("Solo instructores pueden crear cursos")
        
        instructor_id = serializer.validated_data.get('instructor_id')
        
        if self.request.user.perfil == 'administrador':
            # Admin puede asignar cualquier instructor o dejarlo vacío
            if instructor_id:
                instructor = User.objects.get(id=instructor_id)
                serializer.save(instructor=instructor)
            else:
                # Si no especifica instructor, lo deja vacío
                serializer.save(instructor=None)
        else:
            # Instructores solo pueden asignarse a sí mismos
            if instructor_id and instructor_id != self.request.user.id:
                raise permissions.PermissionDenied("Los instructores solo pueden crear cursos para sí mismos")
            serializer.save(instructor=self.request.user)
    
    def perform_update(self, serializer):
        # Solo el propietario o admin pueden editar
        if not CustomPermission.es_propietario_o_admin(self.request.user, self.get_object()):
            raise permissions.PermissionDenied("No tienes permisos para editar este curso")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Solo el propietario o admin pueden eliminar
        if not CustomPermission.es_propietario_o_admin(self.request.user, instance):
            raise permissions.PermissionDenied("No tienes permisos para eliminar este curso")
        # En lugar de eliminar, marcar como inactivo
        instance.activo = False
        instance.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def inscribirse(self, request, pk=None):
        """Inscribir al usuario en el curso"""
        from inscripciones.models import Inscripcion
        from inscripciones.serializers import InscripcionSerializer
        
        curso = self.get_object()
        
        if request.user.perfil != 'estudiante':
            return Response(
                {'error': 'Solo los estudiantes pueden inscribirse en cursos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inscripcion, created = Inscripcion.objects.get_or_create(
            usuario=request.user,
            curso=curso
        )
        
        if not created:
            return Response(
                {'error': 'Ya estás inscrito en este curso'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = InscripcionSerializer(inscripcion, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mis_cursos(self, request):
        """Obtener los cursos del instructor autenticado"""
        if not CustomPermission.es_instructor_o_admin(request.user):
            return Response(
                {'error': 'Solo instructores pueden acceder a esta función'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        cursos = Curso.objects.filter(instructor=request.user)
        serializer = self.get_serializer(cursos, many=True)
        return Response(serializer.data)
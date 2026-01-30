from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum, Avg, Count
from rest_framework import viewsets, status, permissions, exceptions
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
    
    def get_queryset(self):
        # Para mis_cursos: todos los cursos del instructor autenticado (activos e inactivos)
        if self.action == 'mis_cursos':
            if self.request.user.is_authenticated:
                return Curso.objects.filter(instructor=self.request.user)
            return Curso.objects.none()
        
        # Para retrieve (detalle): permitir al instructor ver sus propios cursos inactivos
        if self.action == 'retrieve':
            if self.request.user.is_authenticated:
                if self.request.user.perfil == 'administrador':
                    return Curso.objects.all()
                # Instructores pueden ver cursos activos públicos O sus propios cursos (activos e inactivos)
                return Curso.objects.filter(
                    Q(activo=True) | Q(instructor=self.request.user)
                )
            # Usuarios no autenticados solo ven cursos activos
            return Curso.objects.filter(activo=True)
        
        # Para acciones de modificación/estadísticas: solo cursos del instructor o admin
        if self.action in ['update', 'partial_update', 'destroy', 'estadisticas', 'desactivar', 'activar']:
            if self.request.user.is_authenticated:
                if self.request.user.perfil == 'administrador':
                    return Curso.objects.all()
                return Curso.objects.filter(instructor=self.request.user)
            return Curso.objects.none()
        
        # Para list: administradores ven todos, otros solo activos
        if self.action == 'list':
            if self.request.user.is_authenticated and self.request.user.perfil == 'administrador':
                # Admin puede ver todos los cursos y filtrar por activo
                queryset = Curso.objects.all()
                # Respetar el filtro 'activo' si se proporciona en query params
                activo_param = self.request.query_params.get('activo', None)
                if activo_param is not None:
                    # Convertir string a boolean
                    activo_bool = activo_param.lower() in ['true', '1', 'yes']
                    queryset = queryset.filter(activo=activo_bool)
                return queryset
            # Para el público general: solo cursos activos
            return Curso.objects.filter(activo=True)
        
        # Fallback: solo cursos activos
        return Curso.objects.filter(activo=True)
    
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
        if not CustomPermission.es_instructor_o_admin(self.request.user):
            raise exceptions.PermissionDenied("Solo instructores pueden crear cursos")
        
        instructor_id = serializer.validated_data.get('instructor_id')
        
        if self.request.user.perfil == 'administrador':
            if instructor_id:
                instructor = User.objects.get(id=instructor_id)
                serializer.save(instructor=instructor)
            else:
                serializer.save(instructor=None)
        else:
            if instructor_id and instructor_id != self.request.user.id:
                raise permissions.PermissionDenied("Los instructores solo pueden crear cursos para sí mismos")
            serializer.save(instructor=self.request.user)
    
    def perform_update(self, serializer):
        if not CustomPermission.es_propietario_o_admin(self.request.user, self.get_object()):
            raise permissions.PermissionDenied("No tienes permisos para editar este curso")
        
        # Si es administrador y proporciona instructor_id, actualizar el instructor
        instructor_id = self.request.data.get('instructor_id')
        if self.request.user.perfil == 'administrador' and instructor_id is not None:
            try:
                instructor = User.objects.get(id=instructor_id)
                # Remover instructor_id del validated_data si existe para evitar conflictos
                if 'instructor_id' in serializer.validated_data:
                    serializer.validated_data.pop('instructor_id')
                serializer.save(instructor=instructor)
            except User.DoesNotExist:
                raise exceptions.ValidationError("Instructor no encontrado")
        else:
            # Remover instructor_id del validated_data si existe
            if 'instructor_id' in serializer.validated_data:
                serializer.validated_data.pop('instructor_id')
            serializer.save()
    
    def perform_destroy(self, instance):
        """
        Eliminar curso si no tiene contenido relacionado.
        Si tiene estudiantes/módulos/reseñas, solo desactiva (soft delete).
        """
        if not CustomPermission.es_propietario_o_admin(self.request.user, instance):
            raise permissions.PermissionDenied("No tienes permisos para eliminar este curso")
        
        # Verificar si hay estudiantes inscritos
        from inscripciones.models import Inscripcion
        total_estudiantes = Inscripcion.objects.filter(curso=instance).count()
        
        if total_estudiantes > 0:
            raise exceptions.ValidationError({
                'error': f'No puedes eliminar este curso porque tiene {total_estudiantes} estudiante(s) inscrito(s). Solo puedes desactivarlo.',
                'total_estudiantes': total_estudiantes,
                'accion_recomendada': 'Usa el endpoint /desactivar/ en su lugar'
            })
        
        # Verificar si hay módulos con contenido
        total_modulos = instance.modulos.count()
        if total_modulos > 0:
            # Contar secciones en esos módulos
            from secciones.models import Seccion
            total_secciones = Seccion.objects.filter(modulo__curso=instance).count()
            
            raise exceptions.ValidationError({
                'error': f'No puedes eliminar este curso porque tiene {total_modulos} módulo(s) y {total_secciones} sección(es). Elimina primero el contenido o desactiva el curso.',
                'total_modulos': total_modulos,
                'total_secciones': total_secciones,
                'accion_recomendada': 'Usa el endpoint /desactivar/ en su lugar'
            })
        
        # Verificar si hay reseñas (MongoDB)
        from resenas.models import Resena
        total_resenas = Resena.objects(curso_id=instance.id).count()
        
        if total_resenas > 0:
            raise exceptions.ValidationError({
                'error': f'No puedes eliminar este curso porque tiene {total_resenas} reseña(s). Solo puedes desactivarlo.',
                'total_resenas': total_resenas,
                'accion_recomendada': 'Usa el endpoint /desactivar/ en su lugar'
            })
        
        # Si no hay nada relacionado, ELIMINAR FÍSICAMENTE el curso
        instance.delete()
    
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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def desactivar(self, request, pk=None):
        """
        Desactivar curso (ocultarlo del catálogo público).
        Los estudiantes inscritos siguen teniendo acceso.
        """
        curso = self.get_object()
        
        if not CustomPermission.es_propietario_o_admin(request.user, curso):
            raise permissions.PermissionDenied("No tienes permisos para desactivar este curso")
        
        curso.activo = False
        curso.save()
        
        serializer = self.get_serializer(curso)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def activar(self, request, pk=None):
        """
        Activar curso (mostrarlo en el catálogo público).
        """
        curso = self.get_object()
        
        if not CustomPermission.es_propietario_o_admin(request.user, curso):
            raise permissions.PermissionDenied("No tienes permisos para activar este curso")
        
        curso.activo = True
        curso.save()
        
        serializer = self.get_serializer(curso)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mis_cursos(self, request):
        """Obtener los cursos del instructor autenticado"""
        if not CustomPermission.es_instructor_o_admin(request.user):
            return Response(
                {'error': 'Solo instructores pueden acceder a esta función'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Incluir cursos activos e inactivos del instructor
        cursos = Curso.objects.filter(instructor=request.user)
        serializer = self.get_serializer(cursos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def estadisticas(self, request, pk=None):
        """Obtener estadísticas detalladas de un curso"""
        from inscripciones.models import Inscripcion
        from resenas.models import Resena
        
        curso = self.get_object()
        
        # Verificar permisos: solo el instructor del curso o admin
        if curso.instructor != request.user and request.user.perfil != 'administrador':
            return Response(
                {'error': 'No tienes permiso para ver estas estadísticas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Inscripciones
        inscripciones = Inscripcion.objects.filter(curso=curso)
        total_estudiantes = inscripciones.count()
        estudiantes_completados = inscripciones.filter(completado=True).count()
        estudiantes_activos = inscripciones.filter(
            progreso__gt=0,
            progreso__lt=100
        ).count()
        
        # Promedio de progreso
        promedio_progreso = inscripciones.aggregate(
            Avg('progreso')
        )['progreso__avg'] or 0
        
        # Estadísticas de la última semana
        hace_una_semana = datetime.now() - timedelta(days=7)
        nuevos_estudiantes_semana = inscripciones.filter(
            fecha_inscripcion__gte=hace_una_semana
        ).count()
        completados_semana = inscripciones.filter(
            completado=True,
            fecha_completado__gte=hace_una_semana,
            fecha_completado__isnull=False
        ).count()
        
        # Reseñas y ratings
        resenas = list(Resena.objects(curso_id=curso.id))
        total_resenas = len(resenas)
        rating_promedio = 0
        distribucion_ratings = {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
        
        if resenas:
            suma_ratings = sum(r.rating for r in resenas)
            rating_promedio = round(suma_ratings / total_resenas, 2)
            
            # Distribución por estrellas
            for resena in resenas:
                star = str(int(resena.rating))
                distribucion_ratings[star] = distribucion_ratings.get(star, 0) + 1
            
            # Nuevas reseñas última semana (fecha_creacion es UTC)
            hace_una_semana_utc = datetime.utcnow() - timedelta(days=7)
            nuevas_resenas_semana = sum(
                1 for r in resenas 
                if r.fecha_creacion and r.fecha_creacion >= hace_una_semana_utc
            )
        else:
            nuevas_resenas_semana = 0
        
        # Ingresos
        ingresos_totales = curso.precio * total_estudiantes
        
        return Response({
            'total_estudiantes': total_estudiantes,
            'estudiantes_activos': estudiantes_activos,
            'estudiantes_completados': estudiantes_completados,
            'promedio_progreso': round(promedio_progreso, 2),
            'rating_promedio': rating_promedio,
            'total_resenas': total_resenas,
            'distribucion_ratings': distribucion_ratings,
            'nuevos_estudiantes_semana': nuevos_estudiantes_semana,
            'nuevas_resenas_semana': nuevas_resenas_semana,
            'completados_semana': completados_semana,
            'ingresos_totales': float(ingresos_totales),
        })

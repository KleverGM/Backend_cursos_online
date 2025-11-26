from django.contrib.auth import get_user_model, authenticate
from django.db.models import Avg, Sum
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import UsuarioSerializer, UsuarioPublicSerializer, UsuarioResponseSerializer, EstadisticasUsuarioSerializer
from ..permissions import IsOwnerOrAdmin, IsAdminUser

User = get_user_model()


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsuarioSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['perfil', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['fecha_creacion', 'username', 'email']
    ordering = ['-fecha_creacion']
    
    def get_permissions(self):
        """
        Configurar permisos por acción:
        - create: Solo registro público (se maneja por endpoint separado)
        - list/retrieve: Usuario autenticado
        - update/partial_update/destroy: Solo administradores o el mismo usuario
        """
        if self.action == 'create':
            # El registro se maneja por endpoint separado, aquí solo admin
            permission_classes = [IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Solo administradores pueden crear usuarios vía API"""
        if self.request.user.perfil != 'administrador':
            raise PermissionDenied("Solo administradores pueden crear usuarios")
        serializer.save()
    
    def perform_update(self, serializer):
        """Solo administradores o el mismo usuario pueden actualizar"""
        if (self.request.user.perfil != 'administrador' and 
            self.request.user.id != self.get_object().id):
            raise PermissionDenied("Sin permisos para actualizar este usuario")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Solo administradores pueden eliminar usuarios"""
        if self.request.user.perfil != 'administrador':
            raise PermissionDenied("Solo administradores pueden eliminar usuarios")
        instance.delete()
    
    def get_queryset(self):
        if self.request.user.perfil == 'administrador':
            return User.objects.all()
        else:
            # Los usuarios normales solo pueden ver información pública
            return User.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve'] and self.request.user.perfil != 'administrador':
            return UsuarioPublicSerializer
        return UsuarioSerializer
    
    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """Obtener el perfil del usuario autenticado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas del usuario autenticado"""
        from inscripciones.models import Inscripcion
        from secciones.models import ProgresoSeccion
        from cursos.serializers import CursoSerializer
        
        user = request.user
        inscripciones = Inscripcion.objects.filter(usuario=user)
        
        estadisticas = {
            'total_cursos_inscritos': inscripciones.count(),
            'cursos_completados': inscripciones.filter(completado=True).count(),
            'progreso_promedio': inscripciones.aggregate(
                promedio=Avg('progreso')
            )['promedio'] or 0,
            'total_tiempo_estudiado': ProgresoSeccion.objects.filter(
                usuario=user
            ).aggregate(total=Sum('tiempo_visto'))['total'] or 0,
            'cursos_recientes': CursoSerializer(
                [i.curso for i in inscripciones.order_by('-fecha_inscripcion')[:5]], 
                many=True
            ).data
        }
        
        serializer = EstadisticasUsuarioSerializer(estadisticas)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Registro de nuevo usuario"""
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Crear tokens JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Usuario creado exitosamente',
            'user': UsuarioResponseSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login de usuario"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Permitir login con username o email
    if not password:
        return Response({
            'error': 'Password es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not username and not email:
        return Response({
            'error': 'Username o email son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Intentar autenticar con email primero (es el USERNAME_FIELD)
    user = None
    if email:
        user = authenticate(username=email, password=password)
    
    # Si no funciona con email, intentar con username
    if not user and username:
        try:
            # Buscar el usuario por username y obtener su email
            user_obj = User.objects.get(username=username)
            user = authenticate(username=user_obj.email, password=password)
        except User.DoesNotExist:
            pass
    
    if user and user.is_active:
        # Crear tokens JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login exitoso',
            'user': UsuarioResponseSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Credenciales inválidas'
    }, status=status.HTTP_401_UNAUTHORIZED)
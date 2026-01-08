from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import Resena, Respuesta
from ..serializers import ResenaSerializer
from ..permissions import IsOwnerOrReadOnly
from datetime import datetime


class ResenaViewSet(viewsets.ViewSet):
    """ViewSet para gestionar reseñas de cursos"""
    
    def get_permissions(self):
        """Permisos según la acción"""
        if self.action in ['list', 'retrieve', 'estadisticas_curso']:
            return [AllowAny()]
        elif self.action in ['create', 'marcar_util', 'mis_resenas']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action == 'responder':
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def list(self, request):
        """Listar reseñas (con filtro por curso)"""
        curso_id = request.query_params.get('curso_id')
        
        if curso_id:
            resenas = Resena.objects(curso_id=int(curso_id)).order_by('-fecha_creacion')
        else:
            resenas = Resena.objects.all().order_by('-fecha_creacion')
        
        # Paginación simple
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        resenas_page = list(resenas[start:end])
        serializer = ResenaSerializer(resenas_page, many=True, context={'request': request})
        
        return Response({
            'count': resenas.count(),
            'results': serializer.data
        })
    
    def create(self, request):
        """Crear nueva reseña"""
        serializer = ResenaSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            resena = serializer.save()
            return Response(
                ResenaSerializer(resena, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """Obtener detalle de una reseña"""
        try:
            resena = Resena.objects.get(pk=pk)
            serializer = ResenaSerializer(resena, context={'request': request})
            return Response(serializer.data)
        except Resena.DoesNotExist:
            return Response(
                {'error': 'Reseña no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def update(self, request, pk=None):
        """Actualizar reseña completa"""
        try:
            resena = Resena.objects.get(pk=pk)
            
            # Verificar que sea el autor o admin
            if resena.usuario_id != request.user.id and request.user.perfil != 'administrador':
                return Response(
                    {'error': 'No tienes permiso para editar esta reseña'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = ResenaSerializer(resena, data=request.data, context={'request': request})
            
            if serializer.is_valid():
                resena = serializer.save()
                return Response(ResenaSerializer(resena, context={'request': request}).data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Resena.DoesNotExist:
            return Response(
                {'error': 'Reseña no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def partial_update(self, request, pk=None):
        """Actualizar parcialmente una reseña"""
        try:
            resena = Resena.objects.get(pk=pk)
            
            if resena.usuario_id != request.user.id and request.user.perfil != 'administrador':
                return Response(
                    {'error': 'No tienes permiso para editar esta reseña'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = ResenaSerializer(
                resena, 
                data=request.data, 
                partial=True, 
                context={'request': request}
            )
            
            if serializer.is_valid():
                resena = serializer.save()
                return Response(ResenaSerializer(resena, context={'request': request}).data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Resena.DoesNotExist:
            return Response(
                {'error': 'Reseña no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def destroy(self, request, pk=None):
        """Eliminar reseña"""
        try:
            resena = Resena.objects.get(pk=pk)
            
            if resena.usuario_id != request.user.id and request.user.perfil != 'administrador':
                return Response(
                    {'error': 'No tienes permiso para eliminar esta reseña'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            resena.delete()
            return Response(
                {'message': 'Reseña eliminada exitosamente'},
                status=status.HTTP_204_NO_CONTENT
            )
        
        except Resena.DoesNotExist:
            return Response(
                {'error': 'Reseña no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def marcar_util(self, request, pk=None):
        """Marcar reseña como útil"""
        try:
            resena = Resena.objects.get(pk=pk)
            usuario_id = request.user.id
            
            if usuario_id in resena.usuarios_util:
                # Ya marcó como útil, quitar voto
                resena.usuarios_util.remove(usuario_id)
                resena.util_count = max(0, resena.util_count - 1)
                mensaje = 'Voto removido'
            else:
                # Agregar voto
                resena.usuarios_util.append(usuario_id)
                resena.util_count += 1
                mensaje = 'Marcado como útil'
            
            resena.save()
            
            return Response({
                'message': mensaje,
                'util_count': resena.util_count
            })
        
        except Resena.DoesNotExist:
            return Response(
                {'error': 'Reseña no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def responder(self, request, pk=None):
        """Agregar respuesta a una reseña (solo instructores)"""
        if request.user.perfil not in ['instructor', 'administrador']:
            return Response(
                {'error': 'Solo instructores pueden responder reseñas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            resena = Resena.objects.get(pk=pk)
            texto = request.data.get('texto')
            
            if not texto:
                return Response(
                    {'error': 'El texto de la respuesta es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            respuesta = Respuesta(
                usuario_id=request.user.id,
                texto=texto,
                fecha=datetime.utcnow()
            )
            
            resena.respuestas.append(respuesta)
            resena.save()
            
            return Response(
                ResenaSerializer(resena, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        except Resena.DoesNotExist:
            return Response(
                {'error': 'Reseña no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def mis_resenas(self, request):
        """Obtener todas las reseñas del usuario actual"""
        resenas = Resena.objects(usuario_id=request.user.id).order_by('-fecha_creacion')
        serializer = ResenaSerializer(list(resenas), many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas_curso(self, request):
        """Estadísticas de reseñas de un curso"""
        curso_id = request.query_params.get('curso_id')
        
        if not curso_id:
            return Response(
                {'error': 'curso_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resenas = list(Resena.objects(curso_id=int(curso_id)))
        
        if not resenas:
            return Response({
                'total_resenas': 0,
                'rating_promedio': 0,
                'distribucion': {
                    '5': 0, '4': 0, '3': 0, '2': 0, '1': 0
                }
            })
        
        # Calcular estadísticas
        total = len(resenas)
        suma_ratings = sum(r.rating for r in resenas)
        promedio = round(suma_ratings / total, 2)
        
        # Distribución por estrellas
        distribucion = {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
        for resena in resenas:
            star = str(int(resena.rating))
            distribucion[star] = distribucion.get(star, 0) + 1
        
        return Response({
            'total_resenas': total,
            'rating_promedio': promedio,
            'distribucion': distribucion
        })
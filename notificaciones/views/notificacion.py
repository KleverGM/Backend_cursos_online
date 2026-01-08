from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from bson import ObjectId
from bson.errors import InvalidId

from notificaciones.models import Notificacion
from notificaciones.serializers import NotificacionSerializer
from notificaciones.permissions import IsOwnerOrAdmin, IsAdminUser
from notificaciones.pagination import NotificacionPagination


class NotificacionViewSet(viewsets.ViewSet):
    """
    ViewSet para gestionar notificaciones de usuarios.
    
    Endpoints:
    - GET /api/notificaciones/ - Listar notificaciones del usuario autenticado
    - POST /api/notificaciones/ - Crear notificación (solo admin)
    - GET /api/notificaciones/<id>/ - Ver detalle de notificación
    - PUT/PATCH /api/notificaciones/<id>/ - Actualizar notificación
    - DELETE /api/notificaciones/<id>/ - Eliminar notificación
    - GET /api/notificaciones/no_leidas/ - Listar solo no leídas
    - POST /api/notificaciones/marcar_leida/<id>/ - Marcar una como leída
    - POST /api/notificaciones/marcar_todas_leidas/ - Marcar todas como leídas
    - GET /api/notificaciones/contador/ - Contador de no leídas
    """
    
    pagination_class = NotificacionPagination
    
    def get_permissions(self):
        """
        Define permisos según la acción.
        Solo administradores pueden crear notificaciones manualmente.
        """
        if self.action == 'create':
            # PRODUCCIÓN: Solo administradores pueden crear notificaciones
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """
        Retorna notificaciones según el rol del usuario.
        Admin ve todas, usuarios ven solo las suyas.
        """
        user = self.request.user
        
        if hasattr(user, 'perfil') and user.perfil == 'administrador':
            return Notificacion.objects.all()
        
        return Notificacion.objects.filter(usuario_id=user.id)
    
    def list(self, request):
        """
        Lista notificaciones del usuario autenticado.
        Admin ve todas, usuarios ven solo las suyas.
        """
        queryset = self.get_queryset()
        
        # Aplicar paginación
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(list(queryset), request)
        
        if page is not None:
            serializer = NotificacionSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = NotificacionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """
        Crea una nueva notificación (solo admin).
        """
        serializer = NotificacionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                notificacion = serializer.save()
                
                # Verificar que se guardó correctamente
                if not notificacion.id:
                    return Response(
                        {'error': 'La notificación no se guardó correctamente en MongoDB'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Enviar notificación por WebSocket
                try:
                    self._enviar_por_websocket(notificacion)
                except Exception as ws_error:
                    print(f"Error al enviar por WebSocket: {ws_error}")
                
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                print(f"Error al guardar notificación: {str(e)}")
                return Response(
                    {'error': f'Error al guardar en MongoDB: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def retrieve(self, request, pk=None):
        """
        Obtiene el detalle de una notificación específica.
        """
        try:
            notificacion = Notificacion.objects.get(id=ObjectId(pk))
        except (InvalidId, Notificacion.DoesNotExist):
            return Response(
                {'error': 'Notificación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar permisos (solo el dueño o admin)
        if not (hasattr(request.user, 'perfil') and request.user.perfil == 'administrador'):
            if notificacion.usuario_id != request.user.id:
                return Response(
                    {'error': 'No tienes permiso para ver esta notificación'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = NotificacionSerializer(notificacion)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """
        Actualiza una notificación (PUT completo).
        """
        return self._update_notificacion(request, pk, partial=False)
    
    def partial_update(self, request, pk=None):
        """
        Actualiza parcialmente una notificación (PATCH).
        """
        return self._update_notificacion(request, pk, partial=True)
    
    def _update_notificacion(self, request, pk, partial=False):
        """
        Método auxiliar para actualizar notificaciones.
        """
        try:
            notificacion = Notificacion.objects.get(id=ObjectId(pk))
        except (InvalidId, Notificacion.DoesNotExist):
            return Response(
                {'error': 'Notificación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar permisos
        user = request.user
        is_admin = hasattr(user, 'perfil') and user.perfil == 'administrador'
        is_owner = notificacion.usuario_id == user.id
        
        if not (is_admin or is_owner):
            return Response(
                {'error': 'No tienes permiso para actualizar esta notificación'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Si es usuario normal, solo puede actualizar 'leida'
        if not is_admin:
            allowed_fields = {'leida'}
            request_fields = set(request.data.keys())
            if not request_fields.issubset(allowed_fields):
                return Response(
                    {'error': 'Solo puedes actualizar el campo "leida"'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = NotificacionSerializer(
            notificacion,
            data=request.data,
            partial=partial
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, pk=None):
        """
        Elimina una notificación.
        """
        try:
            notificacion = Notificacion.objects.get(id=ObjectId(pk))
        except (InvalidId, Notificacion.DoesNotExist):
            return Response(
                {'error': 'Notificación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar permisos
        user = request.user
        is_admin = hasattr(user, 'perfil') and user.perfil == 'administrador'
        is_owner = notificacion.usuario_id == user.id
        
        if not (is_admin or is_owner):
            return Response(
                {'error': 'No tienes permiso para eliminar esta notificación'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notificacion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        """
        Retorna solo las notificaciones no leídas del usuario.
        GET /api/notificaciones/no_leidas/
        """
        queryset = self.get_queryset().filter(leida=False)
        
        # Aplicar paginación
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(list(queryset), request)
        
        if page is not None:
            serializer = NotificacionSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = NotificacionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """
        Marca una notificación como leída.
        POST /api/notificaciones/<id>/marcar_leida/
        """
        try:
            notificacion = Notificacion.objects.get(id=ObjectId(pk))
        except (InvalidId, Notificacion.DoesNotExist):
            return Response(
                {'error': 'Notificación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar permisos
        user = request.user
        is_admin = hasattr(user, 'perfil') and user.perfil == 'administrador'
        is_owner = notificacion.usuario_id == user.id
        
        if not (is_admin or is_owner):
            return Response(
                {'error': 'No tienes permiso para actualizar esta notificación'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notificacion.marcar_como_leida()
        serializer = NotificacionSerializer(notificacion)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        """
        Marca todas las notificaciones del usuario como leídas.
        POST /api/notificaciones/marcar_todas_leidas/
        """
        queryset = self.get_queryset().filter(leida=False)
        
        contador = 0
        for notificacion in queryset:
            notificacion.marcar_como_leida()
            contador += 1
        
        return Response({
            'mensaje': f'{contador} notificaciones marcadas como leídas',
            'total': contador
        })
    
    @action(detail=False, methods=['get'])
    def contador(self, request):
        """
        Retorna el número de notificaciones no leídas.
        GET /api/notificaciones/contador/
        """
        count = self.get_queryset().filter(leida=False).count()
        
        return Response({
            'no_leidas': count
        })
    
    def _enviar_por_websocket(self, notificacion):
        """
        Envía la notificación por WebSocket al usuario correspondiente.
        """
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            # Nombre del grupo: notificaciones_user_{user_id}
            group_name = f"notificaciones_user_{notificacion.usuario_id}"
            
            serializer = NotificacionSerializer(notificacion)
            
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'notificacion_mensaje',
                    'notificacion': serializer.data
                }
            )

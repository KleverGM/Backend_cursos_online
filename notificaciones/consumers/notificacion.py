import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificacionConsumer(AsyncWebsocketConsumer):
    """
    Consumer de WebSocket para notificaciones en tiempo real.
    
    Endpoint: ws://localhost:8000/ws/notificaciones/
    
    Cada usuario se conecta a su propio grupo: notificaciones_user_{user_id}
    """
    
    async def connect(self):
        """
        Se ejecuta cuando un cliente intenta conectarse.
        """
        # Obtener el usuario del scope (autenticado por middleware)
        self.user = self.scope.get('user')
        
        # PRODUCCIÓN: Requerir autenticación
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)  # Código personalizado: no autenticado
            return
        
        # Usar el ID del usuario autenticado
        user_id = self.user.id
        
        # Nombre del grupo privado del usuario
        self.group_name = f"notificaciones_user_{user_id}"
        
        # Unirse al grupo del usuario
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Aceptar la conexión WebSocket
        await self.accept()
        
        # Enviar mensaje de bienvenida
        await self.send(text_data=json.dumps({
            'tipo': 'conexion',
            'mensaje': 'Conectado al sistema de notificaciones',
            'usuario_id': self.user.id if (self.user and self.user.is_authenticated) else None,
            'grupo': self.group_name
        }))
    
    async def disconnect(self, close_code):
        """
        Se ejecuta cuando el cliente se desconecta.
        """
        # Salir del grupo del usuario
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Se ejecuta cuando se recibe un mensaje del cliente.
        Puede usarse para ping/pong o comandos especiales.
        """
        try:
            data = json.loads(text_data)
            tipo = data.get('tipo')
            
            if tipo == 'ping':
                # Responder con pong para mantener conexión viva
                await self.send(text_data=json.dumps({
                    'tipo': 'pong',
                    'timestamp': data.get('timestamp')
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'tipo': 'error',
                'mensaje': 'Formato de mensaje inválido'
            }))
    
    async def notificacion_mensaje(self, event):
        """
        Recibe una notificación desde el channel layer y la envía al cliente.
        Este método es llamado cuando se usa channel_layer.group_send()
        """
        notificacion = event['notificacion']
        
        # Enviar la notificación al WebSocket
        await self.send(text_data=json.dumps({
            'tipo': 'notificacion',
            'data': notificacion
        }))

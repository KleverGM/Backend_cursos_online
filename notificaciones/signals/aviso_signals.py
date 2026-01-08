from django.db.models.signals import post_save
from django.dispatch import receiver
from avisos.models import Aviso
from notificaciones.models import Notificacion
from notificaciones.views.notificacion import NotificacionViewSet
import sys


@receiver(post_save, sender=Aviso)
def notificar_nuevo_aviso(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta al crear un nuevo aviso.
    Notifica al usuario destinatario sobre el nuevo aviso.
    """
    # Desactivar durante tests si no hay MongoDB disponible
    if 'test' in sys.argv:
        return
    
    if created:
        usuario = instance.usuario
        
        # Crear notificación para el usuario
        notificacion = Notificacion(
            usuario_id=usuario.id,
            tipo='aviso_nuevo',
            titulo=f'Nuevo aviso: {instance.titulo}',
            mensaje=f'{instance.descripcion[:200]}...' if len(instance.descripcion) > 200 else instance.descripcion,
            datos_extra={
                'aviso_id': instance.id,
                'titulo': instance.titulo,
                'descripcion': instance.descripcion,
                'tipo_aviso': instance.tipo,
                'fecha_envio': instance.fecha_envio.isoformat() if instance.fecha_envio else None,
            }
        )
        notificacion.save()
        
        # Enviar por WebSocket
        try:
            viewset = NotificacionViewSet()
            viewset._enviar_por_websocket(notificacion)
        except Exception as e:
            print(f"Error al enviar notificación por WebSocket: {e}")

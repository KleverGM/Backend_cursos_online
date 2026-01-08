from django.db.models.signals import post_save
from django.dispatch import receiver
from cursos.models import Curso
from inscripciones.models import Inscripcion
from notificaciones.models import Notificacion
from notificaciones.views.notificacion import NotificacionViewSet
import sys


@receiver(post_save, sender=Curso)
def notificar_curso_actualizado(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta al actualizar un curso.
    Notifica a todos los estudiantes inscritos sobre la actualización.
    No notifica cuando el curso se crea por primera vez.
    """
    # Desactivar durante tests si no hay MongoDB disponible
    if 'test' in sys.argv:
        return
    
    if not created:
        # Obtener todas las inscripciones activas en este curso
        inscripciones = Inscripcion.objects.filter(
            curso=instance,
            completado=False  # Solo notificar a quienes no han completado
        ).select_related('usuario')
        
        # Crear notificación para cada estudiante inscrito
        for inscripcion in inscripciones:
            estudiante = inscripcion.usuario
            
            notificacion = Notificacion(
                usuario_id=estudiante.id,
                tipo='curso_actualizado',
                titulo=f'Actualización en {instance.titulo}',
                mensaje=f'El curso "{instance.titulo}" ha sido actualizado. Revisa el nuevo contenido.',
                datos_extra={
                    'curso_id': instance.id,
                    'inscripcion_id': inscripcion.id,
                    'instructor_id': instance.instructor.id,
                    'accion': 'contenido_actualizado',
                }
            )
            notificacion.save()
            
            # Enviar por WebSocket a cada estudiante
            try:
                viewset = NotificacionViewSet()
                viewset._enviar_por_websocket(notificacion)
            except Exception as e:
                print(f"Error al enviar notificación al estudiante {estudiante.id}: {e}")

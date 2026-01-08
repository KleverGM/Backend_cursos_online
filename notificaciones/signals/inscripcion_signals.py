from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from inscripciones.models import Inscripcion
from notificaciones.models import Notificacion
from notificaciones.views.notificacion import NotificacionViewSet
import sys


@receiver(post_save, sender=Inscripcion)
def notificar_nueva_inscripcion(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta al crear una nueva inscripción.
    Notifica tanto al instructor como al estudiante.
    """
    # Desactivar durante tests si no hay MongoDB disponible
    if 'test' in sys.argv:
        return
    
    if created:
        curso = instance.curso
        instructor = curso.instructor
        estudiante = instance.usuario
        
        # 1. Notificación para el INSTRUCTOR
        notificacion_instructor = Notificacion(
            usuario_id=instructor.id,
            tipo='nueva_inscripcion',
            titulo=f'Nueva inscripción en {curso.titulo}',
            mensaje=f'{estudiante.get_full_name() or estudiante.email} se ha inscrito en tu curso "{curso.titulo}".',
            datos_extra={
                'inscripcion_id': instance.id,
                'curso_id': curso.id,
                'estudiante_id': estudiante.id,
                'estudiante_nombre': estudiante.get_full_name() or estudiante.email,
            }
        )
        notificacion_instructor.save()
        
        # Enviar por WebSocket al instructor
        try:
            viewset = NotificacionViewSet()
            viewset._enviar_por_websocket(notificacion_instructor)
        except Exception as e:
            print(f"Error al enviar notificación al instructor: {e}")
        
        # 2. Notificación de BIENVENIDA para el ESTUDIANTE
        notificacion_estudiante = Notificacion(
            usuario_id=estudiante.id,
            tipo='curso_actualizado',  # Usando este tipo genérico
            titulo=f'¡Bienvenido a {curso.titulo}!',
            mensaje=f'Te has inscrito exitosamente en el curso "{curso.titulo}". ¡Comienza tu aprendizaje ahora!',
            datos_extra={
                'inscripcion_id': instance.id,
                'curso_id': curso.id,
                'instructor_id': instructor.id,
                'instructor_nombre': instructor.get_full_name() or instructor.email,
                'accion': 'inscripcion_confirmada',
            }
        )
        notificacion_estudiante.save()
        
        # Enviar por WebSocket al estudiante
        try:
            viewset = NotificacionViewSet()
            viewset._enviar_por_websocket(notificacion_estudiante)
        except Exception as e:
            print(f"Error al enviar notificación al estudiante: {e}")


@receiver(post_save, sender=Inscripcion)
def notificar_curso_completado(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta al actualizar una inscripción.
    Si el curso se marca como completado, notifica al instructor y felicita al estudiante.
    """
    # Desactivar durante tests si no hay MongoDB disponible
    if 'test' in sys.argv:
        return
    
    if not created and instance.completado:
        # Verificar si acaba de completarse (comparar con estado anterior)
        if instance.tracker.has_changed('completado'):
            curso = instance.curso
            instructor = curso.instructor
            estudiante = instance.usuario
            
            # 1. Notificación para el INSTRUCTOR
            notificacion_instructor = Notificacion(
                usuario_id=instructor.id,
                tipo='curso_completado',
                titulo=f'Curso completado: {curso.titulo}',
                mensaje=f'{estudiante.get_full_name() or estudiante.email} ha completado tu curso "{curso.titulo}". ¡Felicitaciones!',
                datos_extra={
                    'inscripcion_id': instance.id,
                    'curso_id': curso.id,
                    'estudiante_id': estudiante.id,
                    'estudiante_nombre': estudiante.get_full_name() or estudiante.email,
                    'progreso': instance.progreso,
                }
            )
            notificacion_instructor.save()
            
            # Enviar por WebSocket al instructor
            try:
                viewset = NotificacionViewSet()
                viewset._enviar_por_websocket(notificacion_instructor)
            except Exception as e:
                print(f"Error al enviar notificación al instructor: {e}")
            
            # 2. Notificación de FELICITACIÓN para el ESTUDIANTE
            notificacion_estudiante = Notificacion(
                usuario_id=estudiante.id,
                tipo='curso_actualizado',
                titulo=f'¡Felicitaciones! Completaste {curso.titulo}',
                mensaje=f'Has completado exitosamente el curso "{curso.titulo}". ¡Excelente trabajo! Ahora puedes dejar una reseña.',
                datos_extra={
                    'inscripcion_id': instance.id,
                    'curso_id': curso.id,
                    'instructor_id': instructor.id,
                    'progreso': instance.progreso,
                    'accion': 'curso_completado',
                }
            )
            notificacion_estudiante.save()
            
            # Enviar por WebSocket al estudiante
            try:
                viewset = NotificacionViewSet()
                viewset._enviar_por_websocket(notificacion_estudiante)
            except Exception as e:
                print(f"Error al enviar notificación al estudiante: {e}")

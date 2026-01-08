from mongoengine.signals import post_save
from notificaciones.models import Notificacion
from resenas.models import Resena
from notificaciones.views.notificacion import NotificacionViewSet
from cursos.models import Curso
from django.contrib.auth import get_user_model

User = get_user_model()


def notificar_nueva_resena(sender, document, created, **kwargs):
    """
    Signal que se ejecuta al crear una nueva reseña en MongoDB.
    Notifica al instructor del curso sobre la nueva reseña.
    """
    if created:
        try:
            # Obtener el curso y el instructor desde PostgreSQL
            curso = Curso.objects.get(id=document.curso_id)
            instructor = curso.instructor
            usuario = User.objects.get(id=document.usuario_id)
            
            # Obtener nombre del usuario
            nombre_usuario = usuario.get_full_name() if hasattr(usuario, 'get_full_name') and usuario.get_full_name() else usuario.email
            
            # Crear notificación para el instructor
            notificacion = Notificacion(
                usuario_id=instructor.id,
                tipo='nueva_resena',
                titulo=f'Nueva reseña en {curso.titulo}',
                mensaje=f'{nombre_usuario} dejó una reseña de {document.rating} estrellas en tu curso "{curso.titulo}": "{document.comentario[:100]}..."',
                datos_extra={
                    'resena_id': str(document.id),
                    'curso_id': curso.id,
                    'usuario_id': usuario.id,
                    'rating': float(document.rating),
                    'titulo': document.titulo,
                    'comentario': document.comentario[:200],
                }
            )
            notificacion.save()
            
            # Enviar por WebSocket
            try:
                viewset = NotificacionViewSet()
                viewset._enviar_por_websocket(notificacion)
            except Exception as e:
                print(f"Error al enviar notificación por WebSocket: {e}")
        except Exception as e:
            print(f"Error al crear notificación de nueva reseña: {e}")


def notificar_respuesta_resena(sender, document, **kwargs):
    """
    Signal que se ejecuta al actualizar una reseña.
    Si se agrega una nueva respuesta, notifica al estudiante.
    """
    # Verificar si hay respuestas nuevas en el array de respuestas
    if document.respuestas and len(document.respuestas) > 0:
        try:
            curso = Curso.objects.get(id=document.curso_id)
            usuario = User.objects.get(id=document.usuario_id)
            
            # Obtener la última respuesta
            ultima_respuesta = document.respuestas[-1]
            
            # Solo notificar si la respuesta es del instructor (no del mismo usuario)
            if ultima_respuesta.usuario_id != document.usuario_id:
                # Crear notificación para el estudiante
                notificacion = Notificacion(
                    usuario_id=usuario.id,
                    tipo='respuesta_resena',
                    titulo=f'Respuesta a tu reseña en {curso.titulo}',
                    mensaje=f'El instructor de "{curso.titulo}" respondió a tu reseña: "{ultima_respuesta.texto[:100]}..."',
                    datos_extra={
                        'resena_id': str(document.id),
                        'curso_id': curso.id,
                        'instructor_id': curso.instructor.id,
                        'respuesta': ultima_respuesta.texto,
                        'fecha_respuesta': ultima_respuesta.fecha.isoformat() if hasattr(ultima_respuesta.fecha, 'isoformat') else str(ultima_respuesta.fecha),
                    }
                )
                notificacion.save()
                
                # Enviar por WebSocket
                try:
                    viewset = NotificacionViewSet()
                    viewset._enviar_por_websocket(notificacion)
                except Exception as e:
                    print(f"Error al enviar notificación por WebSocket: {e}")
        except Exception as e:
            print(f"Error al crear notificación de respuesta: {e}")


# Conectar signals de MongoEngine
post_save.connect(notificar_nueva_resena, sender=Resena)
post_save.connect(notificar_respuesta_resena, sender=Resena)

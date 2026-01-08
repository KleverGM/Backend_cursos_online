from django.apps import AppConfig


class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificaciones'

    def ready(self):
        # Importar signals para registrarlos
        from notificaciones.signals import (
            inscripcion_signals,
            resena_signals,
            aviso_signals,
            curso_signals
        )

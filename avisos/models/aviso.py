from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Aviso(models.Model):
    """Modelo para avisos y notificaciones del sistema"""
    TIPO_CHOICES = [
        ('aviso', 'Aviso'),
        ('mensaje_sistema', 'Mensaje del Sistema'),
        ('recordatorio', 'Recordatorio'),
        ('urgente', 'Urgente'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avisos')
    titulo = models.CharField(max_length=200, verbose_name='Título del aviso')
    descripcion = models.TextField(verbose_name='Descripción del aviso')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='aviso')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    leido = models.BooleanField(default=False)
    comentario = models.TextField(blank=True, verbose_name='Comentarios adicionales')
    
    class Meta:
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'
        db_table = 'avisos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.get_full_name()}"
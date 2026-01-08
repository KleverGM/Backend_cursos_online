from django.db import models
from modulos.models import Modulo


class Seccion(models.Model):
    """Modelo para las secciones de contenido dentro de los módulos"""
    titulo = models.CharField(max_length=200, verbose_name='Título de la sección')
    contenido = models.TextField(verbose_name='Contenido de texto')
    video_url = models.URLField(blank=True, null=True, verbose_name='URL del video')
    archivo = models.FileField(upload_to='secciones/', blank=True, null=True)
    orden = models.PositiveIntegerField(default=1)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='secciones')
    duracion_minutos = models.PositiveIntegerField(default=0, help_text='Duración en minutos')
    es_preview = models.BooleanField(default=False, help_text='Si es True, la sección es pública como vista previa')
    
    class Meta:
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
        db_table = 'secciones'
        ordering = ['modulo', 'orden']
        unique_together = ['modulo', 'orden']
    
    def __str__(self):
        return f"{self.modulo.titulo} - {self.titulo}"


class ProgresoSeccion(models.Model):
    """Modelo para rastrear el progreso por sección"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(blank=True, null=True)
    tiempo_visto = models.PositiveIntegerField(default=0, help_text='Tiempo visto en segundos')
    
    class Meta:
        verbose_name = 'Progreso de Sección'
        verbose_name_plural = 'Progreso de Secciones'
        db_table = 'progreso_secciones'
        unique_together = ['usuario', 'seccion']
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        if self.completado and not self.fecha_completado:
            self.fecha_completado = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.seccion.titulo}"
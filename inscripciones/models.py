from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cursos.models import Curso

User = get_user_model()


class Inscripcion(models.Model):
    """Modelo para las inscripciones de estudiantes en cursos"""
    fecha_inscripcion = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='inscripciones',
        limit_choices_to={'perfil': 'estudiante'}
    )
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='inscripciones')
    progreso = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        help_text='Porcentaje de progreso (0.00 - 100.00)'
    )
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        db_table = 'inscripciones'
        unique_together = ['usuario', 'curso']
        ordering = ['-fecha_inscripcion']
    
    def save(self, *args, **kwargs):
        if self.progreso >= 100.00 and not self.completado:
            self.completado = True
            self.fecha_completado = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.curso.titulo}"

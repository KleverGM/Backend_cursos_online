from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Curso(models.Model):
    """Modelo para los cursos online"""
    NIVEL_CHOICES = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]
    
    CATEGORIA_CHOICES = [
        ('programacion', 'Programación'),
        ('diseño', 'Diseño'),
        ('marketing', 'Marketing'),
        ('negocios', 'Negocios'),
        ('idiomas', 'Idiomas'),
        ('musica', 'Música'),
        ('fotografia', 'Fotografía'),
        ('otros', 'Otros'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.TextField(verbose_name='Descripción')
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    nivel = models.CharField(max_length=15, choices=NIVEL_CHOICES)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    instructor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='cursos_como_instructor',
        limit_choices_to={'perfil': 'instructor'},
        null=True, 
        blank=True
    )
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    imagen = models.ImageField(upload_to='cursos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        db_table = 'cursos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.titulo

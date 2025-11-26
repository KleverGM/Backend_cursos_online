from django.db import models
from cursos.models import Curso


class Modulo(models.Model):
    """Modelo para los módulos de los cursos"""
    titulo = models.CharField(max_length=200, verbose_name='Título del módulo')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    orden = models.PositiveIntegerField(default=1)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    
    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        db_table = 'modulos'
        ordering = ['curso', 'orden']
        unique_together = ['curso', 'orden']
    
    def __str__(self):
        return f"{self.curso.titulo} - {self.titulo}"

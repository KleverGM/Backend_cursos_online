from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Usuario(AbstractUser):
    PERFIL_CHOICES = [
        ('estudiante', 'Estudiante'),
        ('instructor', 'Instructor'),
        ('administrador', 'Administrador'),
    ]
    
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    perfil = models.CharField(max_length=15, choices=PERFIL_CHOICES, default='estudiante')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Inscripcion
from cursos.models import Curso

User = get_user_model()


class InscripcionModelTest(TestCase):
    """Tests para el modelo Inscripcion"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123',
            perfil='instructor'
        )
        
        self.estudiante = User.objects.create_user(
            username='estudiante',
            email='estudiante@example.com',
            password='testpass123',
            perfil='estudiante'
        )
        
        self.curso = Curso.objects.create(
            titulo='Curso de Python',
            descripcion='Aprende Python desde cero',
            categoria='programacion',
            nivel='principiante',
            instructor=self.instructor
        )
        
        self.inscripcion = Inscripcion.objects.create(
            usuario=self.estudiante,
            curso=self.curso
        )
    
    def test_inscripcion_creation(self):
        """Test de creación de inscripción"""
        self.assertEqual(self.inscripcion.usuario, self.estudiante)
        self.assertEqual(self.inscripcion.curso, self.curso)
        self.assertEqual(self.inscripcion.progreso, 0.00)
        self.assertFalse(self.inscripcion.completado)
    
    def test_inscripcion_str(self):
        """Test del método __str__"""
        expected = f"{self.estudiante.get_full_name()} - Curso de Python"
        self.assertEqual(str(self.inscripcion), expected)
    
    def test_auto_completion(self):
        """Test de completado automático"""
        self.inscripcion.progreso = 100.00
        self.inscripcion.save()
        self.assertTrue(self.inscripcion.completado)
        self.assertIsNotNone(self.inscripcion.fecha_completado)


class InscripcionAPITest(APITestCase):
    """Tests para las APIs de inscripción"""
    
    def test_list_inscripciones(self):
        """Test de listado de inscripciones"""
        response = self.client.get('/api/inscripciones/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
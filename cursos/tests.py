from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Curso

User = get_user_model()


class CursoModelTest(TestCase):
    """Tests para el modelo Curso"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123',
            perfil='instructor'
        )
        
        self.curso = Curso.objects.create(
            titulo='Curso de Python',
            descripcion='Aprende Python desde cero',
            categoria='programacion',
            nivel='principiante',
            instructor=self.instructor,
            precio=99.99
        )
    
    def test_curso_creation(self):
        """Test de creación de curso"""
        self.assertEqual(self.curso.titulo, 'Curso de Python')
        self.assertEqual(self.curso.categoria, 'programacion')
        self.assertEqual(self.curso.nivel, 'principiante')
        self.assertTrue(self.curso.activo)
    
    def test_curso_str(self):
        """Test del método __str__"""
        self.assertEqual(str(self.curso), 'Curso de Python')


class CursoAPITest(APITestCase):
    """Tests para las APIs de curso"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpass123',
            perfil='instructor'
        )
        
        self.curso = Curso.objects.create(
            titulo='Curso de Python',
            descripcion='Aprende Python desde cero',
            categoria='programacion',
            nivel='principiante',
            instructor=self.instructor
        )
        
        # Autenticar cliente para los tests
        self.client.force_authenticate(user=self.instructor)
    
    def test_list_cursos(self):
        """Test de listado de cursos"""
        response = self.client.get('/api/cursos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
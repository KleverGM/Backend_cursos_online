from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Seccion, ProgresoSeccion
from modulos.models import Modulo
from cursos.models import Curso

User = get_user_model()


class SeccionModelTest(TestCase):
    """Tests para el modelo Seccion"""
    
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
        
        self.modulo = Modulo.objects.create(
            titulo='Fundamentos',
            descripcion='Conceptos básicos',
            orden=1,
            curso=self.curso
        )
        
        self.seccion = Seccion.objects.create(
            titulo='Variables',
            contenido='Aprende sobre variables',
            orden=1,
            modulo=self.modulo,
            duracion_minutos=10
        )
    
    def test_seccion_creation(self):
        """Test de creación de sección"""
        self.assertEqual(self.seccion.titulo, 'Variables')
        self.assertEqual(self.seccion.orden, 1)
        self.assertEqual(self.seccion.modulo, self.modulo)
        self.assertEqual(self.seccion.duracion_minutos, 10)
    
    def test_seccion_str(self):
        """Test del método __str__"""
        expected = "Fundamentos - Variables"
        self.assertEqual(str(self.seccion), expected)


class SeccionAPITest(APITestCase):
    """Tests para las APIs de sección"""
    
    def test_list_secciones(self):
        """Test de listado de secciones"""
        response = self.client.get('/api/secciones/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
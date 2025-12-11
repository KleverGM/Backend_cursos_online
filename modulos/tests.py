from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Modulo
from cursos.models import Curso

User = get_user_model()


class ModuloModelTest(TestCase):
    """Tests para el modelo Modulo"""
    
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
    
    def test_modulo_creation(self):
        """Test de creación de módulo"""
        self.assertEqual(self.modulo.titulo, 'Fundamentos')
        self.assertEqual(self.modulo.orden, 1)
        self.assertEqual(self.modulo.curso, self.curso)
    
    def test_modulo_str(self):
        """Test del método __str__"""
        expected = "Curso de Python - Fundamentos"
        self.assertEqual(str(self.modulo), expected)


class ModuloAPITest(APITestCase):
    """Tests para las APIs de módulo"""
    
    def setUp(self):
        """Configurar usuario autenticado para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            perfil='estudiante'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_modulos(self):
        """Test de listado de módulos"""
        response = self.client.get('/api/modulos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
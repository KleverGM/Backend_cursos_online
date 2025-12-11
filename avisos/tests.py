from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Aviso

User = get_user_model()


class AvisoModelTest(TestCase):
    """Tests para el modelo Aviso"""
    
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.aviso = Aviso.objects.create(
            usuario=self.usuario,
            titulo='Aviso de prueba',
            descripcion='Descripción del aviso de prueba',
            tipo='general'
        )
    
    def test_aviso_creation(self):
        """Test de creación de aviso"""
        self.assertEqual(self.aviso.titulo, 'Aviso de prueba')
        self.assertEqual(self.aviso.tipo, 'general')
        self.assertEqual(self.aviso.usuario, self.usuario)
        self.assertFalse(self.aviso.leido)
    
    def test_aviso_str(self):
        """Test del método __str__"""
        expected = f"Aviso de prueba - {self.usuario.get_full_name()}"
        self.assertEqual(str(self.aviso), expected)


class AvisoAPITest(APITestCase):
    """Tests para las APIs de aviso"""
    
    def setUp(self):
        """Configurar usuario autenticado para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            perfil='estudiante'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_avisos(self):
        """Test de listado de avisos"""
        response = self.client.get('/api/avisos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
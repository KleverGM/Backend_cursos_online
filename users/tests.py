from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class UsuarioModelTest(TestCase):
    """Tests para el modelo Usuario"""
    
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_usuario_creation(self):
        """Test de creación de usuario"""
        self.assertEqual(self.usuario.email, 'test@example.com')
        self.assertEqual(self.usuario.perfil, 'estudiante')
        self.assertTrue(self.usuario.is_active)
    
    def test_usuario_str(self):
        """Test del método __str__"""
        expected = "Test User (test@example.com)"
        self.assertEqual(str(self.usuario), expected)


class UsuarioAPITest(APITestCase):
    """Tests para las APIs de usuario"""
    
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login(self):
        """Test de login"""
        response = self.client.post('/api/users/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
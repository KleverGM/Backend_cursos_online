# Backend de Cursos Online

API REST para sistema de gestión de cursos online con Django REST Framework y autenticación JWT.

## Instalación y Ejecución

### Prerrequisitos
- Python 3.11+
- pip

### 1. Clonar repositorio
```bash
git clone https://github.com/KleverGM/seminario_integracion.git
cd seminario_integracion/backend_cursos_online
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Ejecutar servidor
```bash
python manage.py runserver
```

La API estará disponible en: `http://localhost:8000/`

## Autenticación

### Obtener token de acceso

**Registro:**
```bash
POST /api/users/register/
{
  "username": "estudiante1",
  "email": "estudiante@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "tipo_usuario": "estudiante"
}
```

**Login:**
```bash
POST /api/users/login/
{
  "email": "estudiante@example.com",
  "password": "password123"
}
```

**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "estudiante1",
    "email": "estudiante@example.com"
  }
}
```

### Usar token en requests
```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Endpoints de la API

### Autenticación
- `POST /api/users/register/` - Registro de usuario
- `POST /api/users/login/` - Login de usuario
- `POST /api/auth/token/` - Obtener token JWT
- `POST /api/auth/refresh/` - Renovar token

### Usuarios
- `GET /api/users/` - Listar usuarios
- `GET /api/users/{id}/` - Detalle de usuario
- `PUT /api/users/{id}/` - Actualizar usuario
- `GET /api/users/perfil/` - Perfil del usuario autenticado

### Cursos
- `GET /api/cursos/` - Listar cursos
- `POST /api/cursos/` - Crear curso
- `GET /api/cursos/{id}/` - Detalle de curso
- `PUT /api/cursos/{id}/` - Actualizar curso
- `POST /api/cursos/{id}/inscribirse/` - Inscribirse en curso

### Módulos
- `GET /api/modulos/` - Listar módulos
- `POST /api/modulos/` - Crear módulo
- `GET /api/modulos/{id}/` - Detalle de módulo
- `PUT /api/modulos/{id}/` - Actualizar módulo

### Secciones
- `GET /api/secciones/` - Listar secciones
- `POST /api/secciones/` - Crear sección
- `GET /api/secciones/{id}/` - Detalle de sección
- `POST /api/secciones/{id}/marcar_completado/` - Marcar completada

### Inscripciones
- `GET /api/inscripciones/` - Listar inscripciones del usuario
- `GET /api/inscripciones/{id}/` - Detalle de inscripción

### Avisos
- `GET /api/avisos/` - Listar avisos del usuario
- `POST /api/avisos/` - Crear aviso
- `PUT /api/avisos/{id}/` - Actualizar aviso

## Ejemplos de Uso con Token

### 1. Crear un curso (como instructor)
```bash
curl -X POST http://localhost:8000/api/cursos/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Introducción a Python",
    "descripcion": "Aprende los fundamentos de Python",
    "categoria": "programacion",
    "nivel": "principiante",
    "precio": "99.99"
  }'
```

### 2. Listar cursos con filtros
```bash
# Todos los cursos
curl http://localhost:8000/api/cursos/

# Cursos de programación
curl "http://localhost:8000/api/cursos/?categoria=programacion"

# Buscar por título
curl "http://localhost:8000/api/cursos/?search=python"
```

### 3. Inscribirse en un curso
```bash
curl -X POST http://localhost:8000/api/cursos/1/inscribirse/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Crear módulo
```bash
curl -X POST http://localhost:8000/api/modulos/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Fundamentos de Python",
    "descripcion": "Conceptos básicos",
    "orden": 1,
    "curso": 1
  }'
```

### 5. Crear sección
```bash
curl -X POST http://localhost:8000/api/secciones/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Variables y tipos de datos",
    "contenido": "En esta lección aprenderemos...",
    "orden": 1,
    "duracion_minutos": 15,
    "modulo": 1
  }'
```

### 6. Marcar sección completada
```bash
curl -X POST http://localhost:8000/api/secciones/1/marcar_completado/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Ver mis inscripciones
```bash
curl http://localhost:8000/api/inscripciones/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
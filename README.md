# Backend de Cursos Online

## Descripción

API REST para un sistema completo de gestión de cursos online construido con Django REST Framework. El sistema permite la creación y administración de cursos educativos con una estructura jerárquica organizada, gestión de usuarios con diferentes roles, y seguimiento detallado del progreso de aprendizaje.

### Características Principales

**Gestión de Usuarios:**

- Sistema de autenticación basado en JWT (JSON Web Tokens)
- Tres tipos de perfiles: Estudiante, Instructor y Administrador
- Autenticación por email y username
- Registro y gestión de usuarios personalizados

**Sistema de Cursos:**

- Creación y administración de cursos por instructores
- Categorización por área (Programación, Diseño, Marketing, Negocios, Idiomas, Música, Fotografía, Otros)
- Niveles de dificultad (Principiante, Intermedio, Avanzado)
- Gestión de precios e imágenes
- Activación/desactivación de cursos

**Estructura de Contenido:**

- **Cursos**: Nivel superior de organización
- **Módulos**: Agrupación temática dentro de cada curso, con orden secuencial
- **Secciones**: Unidades individuales de contenido con texto, videos, archivos y duración

**Sistema de Inscripciones:**

- Inscripción de estudiantes a cursos
- Seguimiento de progreso por curso (porcentaje 0-100%)
- Marca automática de cursos completados
- Control de unicidad (un estudiante no puede inscribirse dos veces al mismo curso)

**Seguimiento de Progreso:**

- Registro detallado del progreso por sección
- Tiempo visualizado por sección (en segundos)
- Marca de secciones completadas con fecha
- Cálculo automático del progreso general del curso

**Sistema de Avisos:**

- Notificaciones personalizadas por usuario
- Tipos de avisos: General, Relacionado con curso, Sistema, Promoción
- Estado de lectura/no leído
- Gestión de fechas de envío

### Tecnologías Utilizadas

- **Framework**: Django 5.2.8
- **API**: Django REST Framework
- **Autenticación**: Simple JWT
- **Base de datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Base de datos NoSQL**: MongoDB (integración opcional)
- **Filtros**: django-filter
- **CORS**: django-cors-headers
- **Archivos estáticos**: WhiteNoise

## Funcionalidades del Backend

### 1. Gestión de Usuarios y Autenticación

**Registro y Login:**

- Registro de nuevos usuarios con validación de datos
- Login con email o username
- Autenticación basada en JWT (Access y Refresh tokens)
- Verificación y renovación de tokens

**Perfiles de Usuario:**

- **Estudiante**: Puede inscribirse a cursos, ver contenido, marcar progreso
- **Instructor**: Puede crear y administrar sus propios cursos
- **Administrador**: Acceso completo al sistema

**Gestión de Perfil:**

- Ver perfil propio (`GET /api/users/perfil/`)
- Actualizar información personal
- Ver estadísticas personales (cursos inscritos, progreso, tiempo estudiado)

### 2. Sistema de Cursos

**CRUD Completo de Cursos:**

- **Crear**: Instructores pueden crear cursos con título, descripción, categoría, nivel, precio e imagen
- **Leer**: Listado público de cursos activos con filtros y búsqueda
- **Actualizar**: El instructor propietario o administrador puede editar
- **Eliminar**: Desactivación lógica (soft delete) del curso

**Filtros y Búsqueda:**

- Filtrar por categoría, nivel e instructor
- Búsqueda por texto en título y descripción
- Ordenamiento por fecha, título o precio

**Inscripción a Cursos:**

- Estudiantes pueden inscribirse a cursos disponibles
- Control de inscripciones duplicadas
- Vista detallada del curso con módulos y secciones

**Estadísticas de Curso:**

- Total de estudiantes inscritos
- Progreso promedio de los estudiantes
- Información del instructor

### 3. Estructura de Contenido

**Módulos:**

- Creación de módulos dentro de cursos
- Ordenamiento secuencial personalizado
- Agrupación lógica de contenido
- Un módulo pertenece a un curso específico

**Secciones:**

- Contenido multimedia: texto, videos (URL), archivos descargables
- Duración en minutos de cada sección
- Ordenamiento dentro de cada módulo
- Gestión de recursos educativos

**Jerarquía:**

```
Curso
  └── Módulo 1
      ├── Sección 1.1
      ├── Sección 1.2
      └── Sección 1.3
  └── Módulo 2
      ├── Sección 2.1
      └── Sección 2.2
```

### 4. Seguimiento de Progreso

**Progreso por Curso:**

- Cálculo automático del porcentaje completado (0-100%)
- Marca automática cuando se alcanza 100%
- Registro de fecha de completación
- Historial de inscripciones del estudiante

**Progreso por Sección:**

- Seguimiento individual de cada sección vista
- Registro del tiempo visualizado en segundos
- Marca de sección completada con fecha
- Actualización del progreso general del curso

**Marcar Completado:**

- Endpoint para marcar secciones como completadas
- Actualización automática del progreso del curso
- Validación de permisos (solo el estudiante inscrito)

### 5. Sistema de Inscripciones

**Gestión de Inscripciones:**

- Inscripción automática con validación de perfil (solo estudiantes)
- Listado de cursos inscritos por usuario
- Filtrado de inscripciones por estado (completado/en progreso)
- Detalle de inscripción con progreso y fechas

**Control de Acceso:**

- Solo estudiantes pueden inscribirse
- Unicidad: un estudiante no puede inscribirse dos veces al mismo curso
- Verificación de permisos para ver contenido

**Estadísticas de Inscripción:**

- Total de cursos inscritos
- Cursos completados
- Progreso promedio en todos los cursos
- Tiempo total estudiado

### 6. Sistema de Avisos y Notificaciones

**Tipos de Avisos:**

- **General**: Anuncios generales del sistema
- **Curso**: Avisos relacionados con cursos específicos
- **Sistema**: Notificaciones técnicas o de mantenimiento
- **Promoción**: Ofertas y promociones

**Gestión de Avisos:**

- Creación de avisos personalizados por usuario
- Programación de envío con fecha específica
- Marca de leído/no leído
- Comentarios adicionales

**Visualización:**

- Listado de avisos del usuario autenticado
- Filtrado por tipo y estado de lectura
- Ordenamiento por fecha (más recientes primero)

### 7. Permisos y Seguridad

**Control de Acceso:**

- Autenticación requerida para operaciones sensibles
- Validación de permisos por rol de usuario
- Verificación de propiedad de recursos

**Reglas de Negocio:**

- Instructores solo pueden editar sus propios cursos
- Estudiantes solo pueden ver sus propias inscripciones
- Administradores tienen acceso completo
- Endpoints públicos para listado de cursos

**Validaciones:**

- Control de unicidad en inscripciones
- Validación de datos en registro y login
- Verificación de tokens JWT en cada petición
- Límites en valores de progreso (0-100%)

### 8. Filtros y Búsqueda Avanzada

**Disponible en:**

- Usuarios: por perfil, estado activo, búsqueda por nombre/email
- Cursos: por categoría, nivel, instructor, búsqueda en título/descripción
- Inscripciones: por estado de completado
- Avisos: por tipo, estado de lectura

**Ordenamiento:**

- Por fecha de creación
- Por nombre o título
- Por precio (cursos)
- Ordenamiento ascendente o descendente

### 9. API RESTful Completa

**Estándares REST:**

- Verbos HTTP correctos (GET, POST, PUT, PATCH, DELETE)
- Códigos de estado HTTP apropiados
- Respuestas JSON estructuradas
- Paginación en listados

**Endpoints Personalizados:**

- `/api/users/perfil/` - Perfil del usuario actual
- `/api/users/estadisticas/` - Estadísticas del usuario
- `/api/cursos/{id}/inscribirse/` - Inscripción a curso
- `/api/secciones/{id}/marcar_completado/` - Marcar sección completada
- `/api/avisos/{id}/marcar_leido/` - Marcar aviso como leído

**Documentación:**

- ViewSets de Django REST Framework
- Serializers personalizados por acción
- Permisos configurables por endpoint

## Instalación y Ejecución

### Prerrequisitos

- Python 3.11+
- pip

### 1. Clonar repositorio

```bash
git https://github.com/KleverGM/Backend_cursos_online.git
cd backend_cursos_online
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
.venv\Scripts\activate
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

## Integración y Despliegue Continuo (CI/CD)

El proyecto cuenta con un pipeline automatizado de CI/CD implementado con GitHub Actions que se ejecuta automáticamente en cada cambio al código.

### Triggers

El workflow se activa en las siguientes situaciones:

1. **Push**: Cuando se sube código a la rama `main` del repositorio
2. **Pull Request**: Cuando se realiza una solicitud de cambios a la rama `main` del repositorio

### Job: Test

Este job se ejecuta en cada push o pull request para validar que el código funciona correctamente:

**Configuración:**

- **Entorno**: Ubuntu Latest
- **Base de datos temporal**: PostgreSQL 16 con health checks
- **Python**: 3.12

**Pasos del Job:**

1. **Checkout del código**: Descarga el código del repositorio
2. **Configuración de Python**: Instala Python 3.12
3. **Instalación de dependencias**: Instala todas las dependencias desde `requirements.txt`
4. **Ejecución de tests**: Ejecuta la suite de tests de Django con las siguientes variables de entorno:
   - Base de datos PostgreSQL temporal
   - Secret key de prueba
   - Configuración de hosts permitidos

**Servicio PostgreSQL:**

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432
```

### Job: Deploy

Este job se ejecuta **solo si el job de test es exitoso** y **solo en la rama main**:

**Requisitos:**

- El job `test` debe completarse exitosamente
- El push/merge debe ser hacia la rama `main` o `master`

**Pasos del Deployment:**

1. **Setup SSH**: Configura las credenciales SSH para conectarse al servidor VPS
2. **Conexión al VPS**: Se conecta al servidor usando las credenciales almacenadas en GitHub Secrets
3. **Actualización de código**:
   - Hace pull del código más reciente desde `origin/main`
   - Reinicia el código a la última versión
4. **Activación del entorno virtual**: Activa el virtualenv de Python en el servidor
5. **Instalación de dependencias**: Actualiza las dependencias desde `requirements.txt`
6. **Migraciones**: Aplica las migraciones de base de datos pendientes
7. **Archivos estáticos**: Recolecta los archivos estáticos
8. **Reinicio del servicio**: Reinicia el servicio de la aplicación

**Secrets Requeridos:**

- `VPS_SSH_KEY`: Clave SSH privada para acceder al servidor
- `VPS_HOST`: Dirección IP o dominio del servidor
- `VPS_USERNAME`: Usuario SSH del servidor
- `DEPLOY_PATH`: Ruta de deployment en el servidor
- `PROJECT_PATH`: Ruta del proyecto en el servidor
- `VENV_PATH`: Ruta del entorno virtual en el servidor

### Beneficios del CI/CD

✅ **Automatización**: Despliegue automático sin intervención manual  
✅ **Calidad**: Tests automáticos antes de cada deployment  
✅ **Confiabilidad**: Validación de PostgreSQL antes de desplegar  
✅ **Rapidez**: Deployment inmediato al hacer merge a main  
✅ **Seguridad**: Credenciales protegidas con GitHub Secrets  
✅ **Trazabilidad**: Historial completo de deployments en GitHub Actions

### Archivo de Configuración

El workflow está definido en: `.github/workflows/deploy.yml`

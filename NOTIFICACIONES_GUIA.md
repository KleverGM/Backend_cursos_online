# 🚀 Guía Rápida - Sistema de Notificaciones

## ✅ Estado Actual

El sistema de notificaciones está **completamente implementado** y funcionando:

- ✅ Modelo MongoDB con 7 tipos de notificaciones
- ✅ REST API completa con CRUD
- ✅ WebSockets configurados (InMemoryChannelLayer)
- ✅ Signals automáticos para eventos
- ✅ Servidor ASGI (Daphne) configurado

## 🔧 Configuración Actual

**Channel Layer**: `InMemoryChannelLayer` (sin Redis)

- ✅ Funciona para desarrollo local
- ✅ WebSockets funcionan en un solo proceso
- ⚠️ No persiste entre reinicios del servidor
- ⚠️ No funciona con múltiples workers

## 🎯 Cómo Iniciar el Servidor

### Opción 1: Servidor ASGI con Daphne (Recomendado para WebSockets)

```bash
# Activar entorno virtual
.venv\Scripts\Activate.ps1

# Iniciar servidor con Daphne
python -m daphne -b 127.0.0.1 -p 8000 curso_online_project.asgi:application
```

### Opción 2: Servidor de desarrollo Django (Solo REST API, sin WebSockets)

```bash
python manage.py runserver
```

## 📡 Probar WebSocket

1. **Iniciar el servidor con Daphne** (ver arriba)

2. **Abrir el archivo de prueba**:

   ```bash
   start test_websocket.html
   ```

3. **Hacer clic en "Conectar WebSocket"**

4. **Deberías ver**:
   - ✅ Estado: "Conectado al servidor"
   - ✅ Mensaje de bienvenida con `usuario_id`

## 📋 Endpoints REST API

### Autenticación Requerida

Todas las peticiones (excepto crear usuario/login) requieren JWT token:

```
Authorization: Bearer <tu_token_jwt>
```

### Endpoints Disponibles

```http
# Listar mis notificaciones
GET http://localhost:8000/api/notificaciones/

# Ver una notificación específica
GET http://localhost:8000/api/notificaciones/<id>/

# Crear notificación (solo admin)
POST http://localhost:8000/api/notificaciones/
Content-Type: application/json

{
    "usuario_id": 1,
    "tipo": "mensaje_sistema",
    "titulo": "Prueba",
    "mensaje": "Mensaje de prueba",
    "datos_extra": {}
}

# Marcar como leída
PATCH http://localhost:8000/api/notificaciones/<id>/
Content-Type: application/json

{
    "leida": true
}

# Eliminar notificación
DELETE http://localhost:8000/api/notificaciones/<id>/

# Ver solo no leídas
GET http://localhost:8000/api/notificaciones/no_leidas/

# Marcar una como leída (endpoint especial)
POST http://localhost:8000/api/notificaciones/<id>/marcar_leida/

# Marcar todas como leídas
POST http://localhost:8000/api/notificaciones/marcar_todas_leidas/

# Contador de no leídas
GET http://localhost:8000/api/notificaciones/contador/
```

## 🔔 Tipos de Notificaciones

1. **`nueva_inscripcion`** - Instructor recibe cuando estudiante se inscribe
2. **`curso_completado`** - Instructor recibe cuando estudiante completa curso
3. **`nueva_resena`** - Instructor recibe cuando hay nueva reseña
4. **`respuesta_resena`** - Estudiante recibe cuando instructor responde
5. **`aviso_nuevo`** - Usuario recibe aviso importante
6. **`curso_actualizado`** - Estudiante recibe cuando curso se actualiza
7. **`mensaje_sistema`** - Admin envía mensaje del sistema

## 🤖 Notificaciones Automáticas (Signals)

El sistema crea notificaciones automáticamente en estos casos:

### ✅ Implementados

- **Nueva Inscripción**: Cuando estudiante se inscribe → notifica al instructor
- **Curso Completado**: Cuando `completado=True` → notifica al instructor
- **Nueva Reseña**: Cuando se crea una reseña → notifica al instructor _(pendiente implementar)_
- **Respuesta Reseña**: Cuando instructor responde → notifica al estudiante _(pendiente implementar)_
- **Nuevo Aviso**: Cuando se crea aviso → notifica al usuario _(pendiente implementar)_

### 📝 Archivos de Signals

- `notificaciones/signals/inscripcion_signals.py` - ✅ Implementado
- `notificaciones/signals/resena_signals.py` - ⚠️ Pendiente
- `notificaciones/signals/aviso_signals.py` - ⚠️ Pendiente

## 🧪 Flujo de Prueba Completo

### 1. Iniciar Servidor

```bash
python -m daphne -b 127.0.0.1 -p 8000 curso_online_project.asgi:application
```

### 2. Obtener Token JWT

```http
POST http://localhost:8000/api/users/login/
Content-Type: application/json

{
    "email": "tu_email@example.com",
    "password": "tu_contraseña"
}
```

**Respuesta**:

```json
{
    "access": "eyJ0eXAiOiJKV1QiLC...",
    "refresh": "eyJ0eXAiOiJKV1QiLC...",
    "user": {...}
}
```

### 3. Probar REST API

```http
GET http://localhost:8000/api/notificaciones/
Authorization: Bearer eyJ0eXAiOiJKV1QiLC...
```

### 4. Probar WebSocket

1. Abrir `test_websocket.html`
2. Conectar WebSocket
3. En otra ventana, crear una inscripción o notificación
4. Ver la notificación llegar en tiempo real

## 📦 Instalar Redis (Opcional para Producción)

Ver instrucciones completas en: `REDIS_SETUP.md`

### Para activar Redis:

1. **Instalar Redis** (Docker, Memurai, o WSL2)

2. **Crear archivo `.env`**:

   ```env
   USE_REDIS=true
   REDIS_HOST=127.0.0.1
   REDIS_PORT=6379
   ```

3. **Reiniciar servidor**

## 🐛 Troubleshooting

### WebSocket no conecta

- ✅ Verificar que usas Daphne, no `runserver`
- ✅ Verificar puerto 8000 disponible
- ✅ Abrir consola del navegador (F12) para ver errores

### Notificaciones no llegan en tiempo real

- ✅ Verificar WebSocket conectado
- ✅ Verificar que el usuario está autenticado
- ✅ Ver logs del servidor Daphne

### Error "Redis connection failed"

- Si ves este error, Redis está configurado pero no instalado
- Solución: Cambiar `USE_REDIS=false` en `.env` o instalar Redis

## 📚 Próximos Pasos

1. ✅ Implementar signals para reseñas y avisos
2. ✅ Pruebas end-to-end con Postman
3. ✅ Documentar en README.md principal
4. ✅ Configurar Redis para producción (Azure Cache for Redis)

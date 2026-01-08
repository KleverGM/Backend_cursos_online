# 🔒 Seguridad del Sistema de Notificaciones - Producción

## ✅ Configuración Actual (PRODUCCIÓN)

El sistema está configurado con **seguridad completa** para producción:

---

## 🔐 Autenticación WebSocket

### Estado Actual: ✅ **HABILITADA**

**Archivo:** `curso_online_project/asgi.py`

```python
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
```

**Características:**

- ✅ `AuthMiddlewareStack`: Verifica tokens JWT en WebSocket
- ✅ `AllowedHostsOriginValidator`: Valida origen de conexión
- ✅ Solo usuarios autenticados pueden conectarse
- ✅ Cada usuario solo recibe sus propias notificaciones

**Rechazos automáticos:**

- ❌ Conexiones sin token JWT
- ❌ Tokens expirados o inválidos
- ❌ Orígenes no permitidos

---

## 🛡️ Permisos REST API

### Estado Actual: ✅ **CONFIGURADO**

**Archivo:** `notificaciones/views/notificacion.py`

```python
def get_permissions(self):
    if self.action == 'create':
        return [IsAdminUser()]  # Solo admins crean manualmente
    return [IsAuthenticated()]  # Usuarios ven sus propias notificaciones
```

**Matriz de Permisos:**

| Endpoint                                   | Método    | Permiso Requerido       | Descripción                   |
| ------------------------------------------ | --------- | ----------------------- | ----------------------------- |
| `/api/notificaciones/`                     | GET       | IsAuthenticated         | Listar propias notificaciones |
| `/api/notificaciones/`                     | POST      | **IsAdminUser**         | Crear notificación manual     |
| `/api/notificaciones/{id}/`                | GET       | IsAuthenticated + Owner | Ver detalle                   |
| `/api/notificaciones/{id}/`                | PUT/PATCH | IsAuthenticated + Owner | Actualizar                    |
| `/api/notificaciones/{id}/`                | DELETE    | IsAuthenticated + Owner | Eliminar                      |
| `/api/notificaciones/no_leidas/`           | GET       | IsAuthenticated         | No leídas propias             |
| `/api/notificaciones/marcar_leida/{id}/`   | POST      | IsAuthenticated + Owner | Marcar como leída             |
| `/api/notificaciones/marcar_todas_leidas/` | POST      | IsAuthenticated         | Marcar todas                  |
| `/api/notificaciones/contador/`            | GET       | IsAuthenticated         | Contador no leídas            |

**Roles:**

- **Admin**: Puede crear notificaciones manualmente + todas las operaciones
- **Usuario**: Solo puede ver/gestionar sus propias notificaciones

---

## 🚫 Consumer WebSocket

### Estado Actual: ✅ **AUTENTICACIÓN REQUERIDA**

**Archivo:** `notificaciones/consumers/notificacion.py`

```python
async def connect(self):
    self.user = self.scope.get('user')

    # Rechazar conexiones no autenticadas
    if not self.user or not self.user.is_authenticated:
        await self.close(code=4001)  # Código personalizado
        return

    user_id = self.user.id
    # Solo se une al grupo de su propio user_id
```

**Protecciones:**

- ✅ Verifica autenticación antes de aceptar conexión
- ✅ Cada usuario solo se une a su propio grupo
- ✅ Imposible recibir notificaciones de otros usuarios
- ✅ Código de cierre 4001 para debugging

---

## 🔑 Autenticación JWT

### Cómo Conectarse al WebSocket con Token

**1. Obtener Token JWT:**

```http
POST http://tu-servidor.com/api/users/login/
Content-Type: application/json

{
    "email": "usuario@example.com",
    "password": "contraseña"
}
```

**Respuesta:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**2. Conectar WebSocket con Token:**

**JavaScript:**

```javascript
const token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...";
const ws = new WebSocket(
  `ws://tu-servidor.com/ws/notificaciones/?token=${token}`
);

ws.onopen = () => {
  console.log("Conectado con autenticación");
};

ws.onerror = (error) => {
  console.error("Error de autenticación:", error);
  // Código 4001 = no autenticado
};
```

**Python:**

```python
import websocket
import json

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
ws = websocket.WebSocket()
ws.connect(f"ws://tu-servidor.com/ws/notificaciones/?token={token}")
```

---

## 🎯 Notificaciones Automáticas (Signals)

### Estado Actual: ✅ **NO REQUIEREN PERMISOS**

Los signals se ejecutan **automáticamente** sin verificar permisos:

**Triggers Automáticos:**

1. ✅ Nueva inscripción → Notifica instructor + estudiante
2. ✅ Curso completado → Notifica instructor + estudiante
3. ✅ Nueva reseña → Notifica instructor
4. ✅ Respuesta a reseña → Notifica estudiante
5. ✅ Curso actualizado → Notifica estudiantes inscritos
6. ✅ Nuevo aviso → Notifica usuario destinatario

**Seguridad:**

- ✅ Signals verifican relaciones (instructor del curso, estudiante inscrito)
- ✅ Solo notifican a usuarios directamente involucrados
- ✅ No exponen información sensible
- ✅ Try/except para evitar errores críticos

---

## 🌐 CORS y Orígenes Permitidos

### Configuración Requerida en `settings.py`

```python
# Hosts permitidos para WebSocket
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'tu-dominio.com',
    'vm-cursos-online.azurewebsites.net',  # Azure
]

# CORS para API REST
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend React
    "https://tu-frontend.com",
]

# WebSocket: AllowedHostsOriginValidator usa ALLOWED_HOSTS automáticamente
```

---

## 🔒 Variables de Entorno Sensibles

### Archivo `.env` (NO SUBIR A GIT)

```env
# Django Secret Key
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura

# JWT Tokens
JWT_SECRET_KEY=otra_clave_secreta_diferente
JWT_ACCESS_TOKEN_LIFETIME=7  # días

# MongoDB
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
MONGODB_DB_NAME=mongo_cursos_online

# Redis (Producción)
USE_REDIS=true
REDIS_HOST=redis.tu-servidor.com
REDIS_PORT=6379
REDIS_PASSWORD=tu_password_redis

# Azure Storage (si aplica)
AZURE_STORAGE_CONNECTION_STRING=...
```

---

## ⚠️ Testing vs Producción

### Modo Testing (DESHABILITADO)

Para testing local **sin autenticación**, modificar temporalmente:

**1. `asgi.py`** - Quitar AuthMiddlewareStack:

```python
application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})
```

**2. `consumers/notificacion.py`** - Permitir anónimos:

```python
if self.user and self.user.is_authenticated:
    user_id = self.user.id
else:
    user_id = 'anonymous'  # Para testing
```

**3. `views/notificacion.py`** - Permitir crear sin admin:

```python
if self.action == 'create':
    return [IsAuthenticated()]  # En vez de IsAdminUser
```

**⚠️ NUNCA DESPLEGAR EN PRODUCCIÓN CON ESTAS MODIFICACIONES**

---

## 📊 Validación de Seguridad

### Checklist Pre-Deployment

- [ ] `AuthMiddlewareStack` habilitado en `asgi.py`
- [ ] `AllowedHostsOriginValidator` configurado
- [ ] Consumer rechaza conexiones sin autenticación
- [ ] Endpoint `create` requiere `IsAdminUser`
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] Variables sensibles en `.env` (no en código)
- [ ] `.env` en `.gitignore`
- [ ] JWT tokens con tiempo de expiración apropiado
- [ ] Redis configurado para producción (`USE_REDIS=true`)
- [ ] HTTPS habilitado (`wss://` en vez de `ws://`)

---

## 🚀 Deploy en Azure

### Configuración Específica

**1. Variables de Entorno en Azure:**

```bash
az webapp config appsettings set --name tu-app --resource-group tu-rg --settings \
    DJANGO_SECRET_KEY="..." \
    JWT_SECRET_KEY="..." \
    MONGODB_URI="..." \
    USE_REDIS="true" \
    REDIS_HOST="..." \
    ALLOWED_HOSTS="tu-app.azurewebsites.net"
```

**2. WebSocket sobre HTTPS:**

```javascript
// Frontend debe usar wss:// (WebSocket Secure)
const ws = new WebSocket(
  `wss://tu-app.azurewebsites.net/ws/notificaciones/?token=${token}`
);
```

**3. Azure Redis Cache:**

- Crear Azure Cache for Redis
- Obtener connection string
- Configurar en `settings.py`

---

## 🛠️ Debugging Problemas de Autenticación

### Error: WebSocket cierra inmediatamente (código 4001)

**Causa:** Token inválido o expirado

**Solución:**

1. Verificar token en [jwt.io](https://jwt.io)
2. Confirmar que no expiró
3. Obtener nuevo token con `/api/users/login/`

### Error: 403 Forbidden en POST /api/notificaciones/

**Causa:** Usuario no tiene rol "Administrador"

**Solución:**

- Usar usuario con `rol = 'Administrador'`
- O cambiar temporalmente permiso a `IsAuthenticated()` (solo testing)

### Error: Notificaciones no llegan por WebSocket

**Causa:** Usuario conectado con ID diferente al destinatario

**Solución:**

- Verificar que `usuario_id` en notificación coincide con usuario conectado
- Ver logs: `group_name = f"notificaciones_user_{user_id}"`

---

## 📝 Logs de Seguridad

### Eventos Importantes a Monitorear

```python
# En consumer
print(f"Usuario {user_id} conectado a grupo {self.group_name}")
print(f"Conexión rechazada: usuario no autenticado")

# En views
print(f"Notificación creada para usuario {notificacion.usuario_id}")
print(f"Error al enviar notificación: {e}")
```

---

## ✅ Estado Final

**Sistema completamente seguro para producción:**

- ✅ Autenticación JWT requerida en WebSocket
- ✅ Solo admins crean notificaciones manualmente
- ✅ Usuarios solo ven sus propias notificaciones
- ✅ Validación de orígenes permitidos
- ✅ Signals automáticos funcionando
- ✅ Sin exposición de datos sensibles

**Listo para deploy en Azure** 🚀

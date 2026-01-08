# Azure VM Ubuntu - Gunicorn + Nginx + Daphne (WebSocket)

## 🌐 Tu Deployment Actual

**URL:** https://cursos-online-api.desarrollo-software.xyz/
**Tipo:** Azure VM Ubuntu
**Stack:** Gunicorn (HTTP) + Nginx (Proxy) + **Daphne (WebSocket)**

---

## 📦 Requirements.txt - YA COMPLETO ✅

Todas las dependencias necesarias están en `requirements.txt`.

---

## 🚀 Arquitectura de Deployment

```
Internet → Nginx (80/443)
    ├── HTTP /api/* → Gunicorn :8000 (WSGI - REST API)
    └── WebSocket /ws/* → Daphne :8001 (ASGI - WebSocket)
```

**Dos servicios corriendo:**

1. **Gunicorn** en puerto 8000 - Para HTTP/REST
2. **Daphne** en puerto 8001 - Para WebSocket

---

## 🔧 Configuración de systemd

### 1. Servicio Gunicorn (ya lo tienes)

Verificar `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon for Cursos Online
After=network.target

[Service]
User=tu_usuario
Group=www-data
WorkingDirectory=/home/tu_usuario/backend_cursos_online
ExecStart=/home/tu_usuario/backend_cursos_online/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    curso_online_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2. Servicio Daphne (NUEVO - para WebSocket)

Crear `/etc/systemd/system/daphne.service`:

```ini
[Unit]
Description=Daphne daemon for Cursos Online WebSocket
After=network.target

[Service]
User=tu_usuario
Group=www-data
WorkingDirectory=/home/tu_usuario/backend_cursos_online
EnvironmentFile=/home/tu_usuario/backend_cursos_online/.env
ExecStart=/home/tu_usuario/backend_cursos_online/venv/bin/daphne \
    -b 127.0.0.1 \
    -p 8001 \
    curso_online_project.asgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Comandos para activar:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable daphne.service
sudo systemctl start daphne.service
sudo systemctl status daphne.service
```

---

## 🌐 Configuración de Nginx

Actualizar tu archivo de configuración de Nginx (normalmente en `/etc/nginx/sites-available/cursos_online`):

```nginx
# Upstream para Gunicorn (HTTP)
upstream django_http {
    server 127.0.0.1:8000;
}

# Upstream para Daphne (WebSocket)
upstream django_websocket {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name cursos-online-api.desarrollo-software.xyz;

    # Redirigir HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name cursos-online-api.desarrollo-software.xyz;

    # Certificados SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/cursos-online-api.desarrollo-software.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cursos-online-api.desarrollo-software.xyz/privkey.pem;

    # Archivos estáticos
    location /static/ {
        alias /home/tu_usuario/backend_cursos_online/staticfiles/;
    }

    location /media/ {
        alias /home/tu_usuario/backend_cursos_online/media/;
    }

    # WebSocket - IMPORTANTE: Debe ir ANTES de location /
    location /ws/ {
        proxy_pass http://django_websocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_read_timeout 86400;  # 24 horas
    }

    # HTTP/REST API
    location / {
        proxy_pass http://django_http;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Aplicar cambios:**

```bash
sudo nginx -t  # Verificar sintaxis
sudo systemctl reload nginx
```

---

## 🔒 Variables de Entorno (.env)

En `/home/tu_usuario/backend_cursos_online/.env` agregar:

```bash
# Existentes
DEBUG=False
ALLOWED_HOSTS=cursos-online-api.desarrollo-software.xyz
SECRET_KEY=tu_secret_key
DB_NAME=cursos_online_db
DB_USER=admin_user
DB_PASSWORD=Admin123
DB_HOST=localhost
DB_PORT=5432

# NUEVAS para Notificaciones
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
MONGODB_DB_NAME=mongo_cursos_online
JWT_SECRET_KEY=otra_clave_diferente_muy_larga
USE_REDIS=false

# O si tienes Redis instalado:
# USE_REDIS=true
# REDIS_HOST=localhost
# REDIS_PORT=6379
```

---

## 📋 Proceso de Deployment (Con Deploy Automático)

### Desde tu máquina local:

```powershell
# 1. Commit y push
git add .
git commit -m "Sistema de notificaciones con WebSocket"
git push origin main
```

**Azure ejecutará automáticamente:**
- ✅ Git pull en el servidor
- ✅ Instalación de requirements.txt
- ✅ Migraciones (si está configurado)
- ✅ Collectstatic (si está configurado)

### Una sola vez: Configurar servicio Daphne en VM

**⚠️ Esto solo se hace UNA VEZ** (después del primer push):

SSH a tu VM:
```bash
ssh tu_usuario@cursos-online-api.desarrollo-software.xyz
```

Crear servicio Daphne:
```bash
sudo nano /etc/systemd/system/daphne.service
```

Copiar contenido (ajusta `tu_usuario` y la ruta):
```ini
[Unit]
Description=Daphne daemon for Cursos Online WebSocket
After=network.target

[Service]
User=tu_usuario
Group=www-data
WorkingDirectory=/home/tu_usuario/backend_cursos_online
EnvironmentFile=/home/tu_usuario/backend_cursos_online/.env
ExecStart=/home/tu_usuario/backend_cursos_online/venv/bin/daphne \
    -b 127.0.0.1 \
    -p 8001 \
    curso_online_project.asgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable daphne
sudo systemctl start daphne
```

Actualizar Nginx (agregar bloque `/ws/` de la guía anterior):
```bash
sudo nano /etc/nginx/sites-available/cursos_online
sudo nginx -t
sudo systemctl reload nginx
```

### Deployments futuros:

Solo necesitas:
```powershell
git push origin main
```

Y opcionalmente verificar/reiniciar servicios si es necesario:
```bash
ssh tu_usuario@cursos-online-api.desarrollo-software.xyz
sudo systemctl restart daphne  # Solo si es necesario
```

---

## 🧪 Testing Post-Deployment

### 3. Conectar WebSocket (JavaScript)

```javascript
const token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...";
const ws = new WebSocket(
  `wss://cursos-online-api.desarrollo-software.xyz/ws/notificaciones/?token=${token}`
);

ws.onopen = () => console.log("✅ WebSocket conectado");
ws.onmessage = (event) =>
  console.log("📩 Notificación:", JSON.parse(event.data));
ws.onerror = (error) => console.error("❌ Error:", error);
```

### 4. Probar REST API de Notificaciones

```bash
# Listar notificaciones
curl https://cursos-online-api.desarrollo-software.xyz/api/notificaciones/ \
  -H "Authorization: Bearer TU_TOKEN"

# Contador de no leídas
curl https://cursos-online-api.desarrollo-software.xyz/api/notificaciones/contador/ \
  -H "Authorization: Bearer TU_TOKEN"
```

### 1. Verificar que los servicios están corriendo

```bash
# Ver status
sudo systemctl status gunicorn
sudo systemctl status daphne

# Ver logs en tiempo real
sudo journalctl -u gunicorn -f
sudo journalctl -u daphne -f
```

Deberías ver en los logs de Daphne:

```
Listening on TCP address 127.0.0.1:8001
✓ Conexión exitosa a MongoDB: mongo_cursos_online
```

### 2. Probar REST API (Gunicorn)

```bash
curl https://cursos-online-api.desarrollo-software.xyz/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"tu_password"}'
```

### 3. Probar WebSocket (Daphne)

**JavaScript:**

```javascript
const token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...";
const ws = new WebSocket(
  `wss://cursos-online-api.desarrollo-software.xyz/ws/notificaciones/?token=${token}`
);

ws.onopen = () => console.log("✅ WebSocket conectado");
ws.onmessage = (event) =>
  console.log("📩 Notificación:", JSON.parse(event.data));
ws.onerror = (error) => console.error("❌ Error:", error);
```

### 4. Verificar puertos

```bash
# Ver que ambos servicios están escuchando
sudo netstat -tlnp | grep -E ':(8000|8001)'
```

Deberías ver:

```
tcp  0.0.0.0:8000  LISTEN  gunicorn
tcp  0.0.0.0:8001  LISTEN  daphne
```

---

## 🐛 Troubleshooting

### Error: Daphne no inicia

**Verificar logs:**

```bash
sudo journalctl -u daphne -n 50
```

**Causa común:** Módulos no instalados

**Solución:**

```bash
cd ~/backend_cursos_online
source venv/bin/activate
pip install channels channels-redis daphne mongoengine blinker django-model-utils
sudo systemctl restart daphne
```

### Error: WebSocket 502 Bad Gateway

**Causa:** Daphne no está corriendo o puerto incorrecto

**Solución:**

```bash
# Verificar que Daphne escucha en 8001
sudo netstat -tlnp | grep 8001

# Verificar logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Reiniciar Daphne
sudo systemctl restart daphne
```

### Error: WebSocket 403 Forbidden

**Causa:** Token JWT inválido o no enviado

**Solución:**

1. Obtener nuevo token: `POST /api/users/login/`
2. Verificar que se envía en URL: `?token=TOKEN`

### Error: MongoDB connection failed

**Causa:** Variable `MONGODB_URI` incorrecta o no configurada

**Solución:**

```bash
# Verificar .env
cat ~/backend_cursos_online/.env | grep MONGODB

# Editar si es necesario
nano ~/backend_cursos_online/.env

# Reiniciar servicios
sudo systemctl restart daphne
```

### Error: Import error en signals

**Causa:** Circular import o módulo mal configurado

**Solución:**

```bash
# Verificar que los signals se cargan
cd ~/backend_cursos_online
source venv/bin/activate
python manage.py shell

>>> from notificaciones.signals import inscripcion_signals
>>> print("OK")
```

---

## 🔒 Seguridad y Firewall

### Puertos en Azure NSG (Network Security Group)

Asegúrate de tener estas reglas:

| Puerto | Protocolo | Descripción |
| ------ | --------- | ----------- |
| 22     | TCP       | SSH         |
| 80     | TCP       | HTTP        |
| 443    | TCP       | HTTPS       |

**NO necesitas** abrir 8000 o 8001 porque Nginx hace el proxy.

### Firewall local (ufw)

```bash
sudo ufw status
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## 📊 Monitoreo

### Ver logs en tiempo real

```bash
# Logs de Daphne (WebSocket)
sudo journalctl -u daphne -f

# Logs de Gunicorn (REST API)
sudo journalctl -u gunicorn -f

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Verificar uso de recursos

```bash
# Ver procesos de Python
ps aux | grep -E 'gunicorn|daphne'

# Ver uso de CPU/Memoria
htop
```

---

## ✅ Checklist Completo

**Archivos de configuración:**

- [ ] `/etc/systemd/system/gunicorn.service` (ya existe)
- [ ] `/etc/systemd/system/daphne.service` (NUEVO)
- [ ] `/etc/nginx/sites-available/cursos_online` (actualizado con /ws/)
- [ ] `~/backend_cursos_online/.env` (con MONGODB_URI, JWT_SECRET_KEY)

**Servicios:**

- [ ] `sudo systemctl enable gunicorn`
- [ ] `sudo systemctl enable daphne`
- [ ] `sudo systemctl status gunicorn` → Active (running)
- [ ] `sudo systemctl status daphne` → Active (running)
- [ ] `sudo systemctl status nginx` → Active (running)

**Testing:**

- [ ] `curl https://cursos-online-api.desarrollo-software.xyz/` → 200 OK
- [ ] `POST /api/users/login/` → Token JWT
- [ ] WebSocket conecta: `wss://cursos-online-api.desarrollo-software.xyz/ws/notificaciones/?token=TOKEN`
- [ ] Notificaciones llegan en tiempo real

**Logs:**

- [ ] Daphne logs: "Listening on TCP address 127.0.0.1:8001"
- [ ] MongoDB: "✓ Conexión exitosa"
- [ ] No hay errores en Nginx error.log

---

## 🚀 Comando de Deploy Completo

Guarda este script en `~/deploy.sh`:

```bash
#!/bin/bash
echo "🚀 Desplegando sistema de notificaciones..."

cd ~/backend_cursos_online
git pull origin main

source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput

sudo systemctl restart gunicorn
sudo systemctl restart daphne
sudo systemctl reload nginx

echo "✅ Deployment completo"
echo "📊 Status de servicios:"
sudo systemctl status gunicorn --no-pager -l
sudo systemctl status daphne --no-pager -l
```

Hacerlo ejecutable:

```bash
chmod +x ~/deploy.sh
```

Usar:

```bash
~/deploy.sh
```

---

## 🎯 URLs Finales

**REST API:**

```
https://cursos-online-api.desarrollo-software.xyz/api/notificaciones/
```

**WebSocket:**

```
wss://cursos-online-api.desarrollo-software.xyz/ws/notificaciones/?token={JWT_TOKEN}
```

**¡Listo para producción!** 🎉

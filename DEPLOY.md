# Guía de Despliegue en Azure

## ✅ Estado actual
- Migraciones ejecutadas correctamente
- Servidor funcionando
- Variables de entorno configuradas en `.env`

## 📋 Tu configuración actual

Tu archivo `.env` en Azure ya está configurado con:
```bash
DEBUG=False
ALLOWED_HOSTS=*
SECRET_KEY=PON_AQUI_UNA_CLAVE_LARGA_Y_COMPLEJA
DB_NAME=cursos_online_db
DB_USER=admin_user
DB_PASSWORD=Admin123
DB_HOST=127.0.0.1
DB_PORT=5432
```

## 🚀 Pasos para desplegar en Azure

### 1. Actualizar el código en Azure
Conéctate por SSH a tu VM de Azure y ejecuta:

```bash
cd ~/cursos_online/Backend_cursos_online
git pull origin main
```

### 2. Activar entorno virtual e instalar dependencias
```bash
source venv/bin/activate
pip install -r requirements.txt
pip install --upgrade setuptools>=81.0
```

### 3. Verificar que tu archivo .env existe
```bash
cat .env
```

Debería mostrar las variables que ya configuraste. Si necesitas editarlo:
```bash
nano .env
```

### 4. Ejecutar migraciones y recopilar estáticos
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Iniciar el servidor con Gunicorn
```bash
bash startup.sh
```

O manualmente:
```bash
gunicorn curso_online_project.wsgi:application \
    --bind=0.0.0.0:8000 \
    --workers=4 \
    --timeout=120 \
    --access-logfile=- \
    --error-logfile=-
```

### 6. (Opcional) Ejecutar como servicio systemd
Para que se inicie automáticamente, puedes crear un servicio:

```bash
sudo nano /etc/systemd/system/django-app.service
```

Contenido:
```ini
[Unit]
Description=Django Cursos Online
After=network.target

[Service]
Type=notify
User=KleverGM
WorkingDirectory=/home/KleverGM/cursos_online/Backend_cursos_online
Environment="PATH=/home/KleverGM/cursos_online/Backend_cursos_online/venv/bin"
ExecStart=/home/KleverGM/cursos_online/Backend_cursos_online/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    curso_online_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

Activar el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable django-app
sudo systemctl start django-app
sudo systemctl status django-app
```

## 🔍 Verificar el despliegue

### Endpoints disponibles:
- Admin: `http://tu-ip:8000/admin/`
- API Users: `http://tu-ip:8000/api/users/`
- API Cursos: `http://tu-ip:8000/api/cursos/`
- API Módulos: `http://tu-ip:8000/api/modulos/`
- API Secciones: `http://tu-ip:8000/api/secciones/`
- API Inscripciones: `http://tu-ip:8000/api/inscripciones/`
- API Avisos: `http://tu-ip:8000/api/avisos/`

**Nota:** El error 404 en la raíz `/` es normal - tu API no tiene una vista raíz configurada.

## ⚠️ Problemas comunes y soluciones

### 1. Warning de `pkg_resources`
```
UserWarning: pkg_resources is deprecated as an API...
```

**Solución:**
```bash
pip install --upgrade setuptools>=81.0
```

### 2. Error de conexión a PostgreSQL
Si ves errores de conexión, verifica:
```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Verificar que la base de datos existe
sudo -u postgres psql -c "\l" | grep cursos_online_db

# Crear base de datos si no existe
sudo -u postgres psql -c "CREATE DATABASE cursos_online_db;"
sudo -u postgres psql -c "CREATE USER admin_user WITH PASSWORD 'Admin123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cursos_online_db TO admin_user;"
```

### 3. Puerto 8000 ya en uso
```bash
# Ver qué proceso está usando el puerto
sudo lsof -i :8000

# Matar el proceso si es necesario
sudo kill -9 <PID>
```

### 4. Permisos en archivos media/static
```bash
# Asegurar permisos correctos
chmod -R 755 staticfiles/
chmod -R 755 media/
```

## 📊 Monitoreo y logs

### Ver logs de Gunicorn en tiempo real
```bash
# Si usas startup.sh directamente
tail -f nohup.out

# Si usas systemd
sudo journalctl -u django-app -f
```

### Ver logs de PostgreSQL
```bash
sudo tail -f /var/log/postgresql/postgresql-*.log
```

## 🔒 Seguridad

### ⚠️ IMPORTANTE antes de producción:

1. **Cambiar SECRET_KEY:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Actualiza el valor en tu `.env`

2. **Configurar ALLOWED_HOSTS correctamente:**
   En lugar de `*`, especifica tu dominio o IP:
   ```bash
   ALLOWED_HOSTS=tu-dominio.com,tu-ip-publica
   ```

3. **Configurar CORS_ALLOWED_ORIGINS:**
   Agrega esto a tu `.env`:
   ```bash
   CORS_ALLOWED_ORIGINS=https://tu-frontend.com
   ```

4. **Habilitar firewall:**
   ```bash
   sudo ufw allow 8000
   sudo ufw allow 22
   sudo ufw enable
   ```

## 📦 Archivos creados/modificados

✅ `requirements.txt` - Dependencias de producción (gunicorn, whitenoise, psycopg2-binary)
✅ `startup.sh` - Script de inicio para Gunicorn
✅ `settings.py` - Configurado para producción con WhiteNoise y seguridad
✅ `.env.example` - Plantilla actualizada con tus variables actuales

## 🚀 Próximos pasos recomendados

1. ✅ Cambiar SECRET_KEY por una nueva
2. ✅ Configurar CORS con el dominio de tu frontend
3. ✅ Configurar Nginx como proxy reverso
4. ✅ Configurar certificado SSL con Let's Encrypt
5. ✅ Configurar backups automáticos de la base de datos
6. ✅ Implementar CI/CD con GitHub Actions
7. ✅ Configurar dominio personalizado
8. ✅ Monitoreo y alertas

## 📝 Notas importantes

- ⚠️ El error 404 en `/` es normal - tu API no tiene una vista raíz configurada
- ⚠️ Asegúrate de que `DEBUG=False` esté en tu `.env` de producción
- ⚠️ Nunca subas el archivo `.env` a Git (ya está en `.gitignore`)
- ✅ WhiteNoise servirá tus archivos estáticos automáticamente
- ✅ Gunicorn maneja múltiples workers para mejor rendimiento
- ✅ La configuración actual usa PostgreSQL local en la VM de Azure

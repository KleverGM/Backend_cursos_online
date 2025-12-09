#!/bin/bash

# Script de inicio para Azure App Service
# Este script ejecuta las migraciones y luego inicia el servidor Gunicorn

echo "Iniciando el despliegue..."

# Aplicar migraciones de base de datos
echo "Aplicando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe (opcional)
# python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

# Iniciar Gunicorn con 4 workers
echo "Iniciando Gunicorn..."
gunicorn curso_online_project.wsgi:application \
    --bind=0.0.0.0:8000 \
    --workers=4 \
    --threads=2 \
    --timeout=120 \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info

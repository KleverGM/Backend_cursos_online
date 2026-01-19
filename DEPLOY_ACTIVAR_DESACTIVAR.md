# Deploy de Corrección: Activar/Desactivar Cursos

## Cambios Realizados

Se corrigieron los endpoints `/activar/` y `/desactivar/` para que devuelvan el curso serializado completo en lugar de solo `{id, activo, message}`.

## Comandos para Deploy en Azure

```bash
# 1. Conectar por SSH
ssh azureuser@<tu-ip-azure>

# 2. Ir al directorio del proyecto
cd /home/azureuser/backend_cursos_online

# 3. Activar entorno virtual
source /home/azureuser/venv/bin/activate

# 4. Hacer pull de los cambios
git pull origin main

# 5. Reiniciar Gunicorn
sudo systemctl restart gunicorn

# 6. Verificar status
sudo systemctl status gunicorn

# 7. Ver logs si hay error
sudo journalctl -u gunicorn -n 50
```

## Verificación

Puedes probar con Postman:

**POST** `https://tu-dominio/api/cursos/{id}/activar/`

Headers:

```
Authorization: Bearer {tu_token}
```

Respuesta esperada (200 OK):

```json
{
  "id": 1,
  "titulo": "Curso 01",
  "descripcion": "...",
  "categoria": "programacion",
  "nivel": "intermedio",
  "precio": "650.00",
  "imagen": "...",
  "activo": true,
  "instructor": {...},
  "total_estudiantes": 5,
  "total_modulos": 0,
  "total_secciones": 0,
  "duracion_total": 0,
  "fecha_creacion": "..."
}
```

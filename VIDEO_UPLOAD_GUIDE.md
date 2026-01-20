# Guía: Subir Videos al Servidor

## 🎯 Problema Resuelto

Muchos videos de YouTube tienen restricciones de reproducción en aplicaciones externas (Error 152-4). Por eso, ahora puedes subir archivos MP4 directamente al servidor sin restricciones.

## 📋 Opciones para Agregar Videos a Secciones

### Opción 1: Subir Archivo MP4 (Recomendado)
- **Ventajas**: Sin restricciones, reproducción garantizada, control total
- **Desventajas**: Requiere espacio en servidor, archivos grandes
- **Uso**: Campo `video_file` en el admin de Django

### Opción 2: URL de YouTube
- **Ventajas**: No ocupa espacio, fácil de agregar
- **Desventajas**: Puede tener restricciones de reproducción
- **Uso**: Campo `video_url` en el admin de Django

## 🚀 Cómo Subir un Video MP4

### Desde el Admin de Django:

1. Ve a la sección de Secciones en el admin
2. Edita o crea una sección
3. En el grupo "Recursos Multimedia":
   - **video_file**: Haz clic en "Elegir archivo" y selecciona tu MP4
   - **video_url**: Deja vacío (o quita la URL de YouTube si había)
4. Guarda la sección

### Desde la API:

```python
import requests

url = "https://cursos-online-api.desarrollo-software.xyz/api/secciones/"
files = {
    'video_file': open('mi_video.mp4', 'rb')
}
data = {
    'titulo': 'Lección con Video',
    'modulo': 1,
    'orden': 1,
    'duracion_minutos': 15
}
response = requests.post(url, files=files, data=data, headers={'Authorization': 'Bearer TOKEN'})
```

## 📱 Comportamiento en la App

El serializer devuelve `video_url_completa` que:
- Si hay `video_file` → Devuelve URL completa del MP4: `https://cursos-online-api.desarrollo-software.xyz/media/videos/mi_video.mp4`
- Si no hay `video_file` → Devuelve `video_url` (YouTube)

La app Flutter detecta automáticamente:
- URLs con "youtube.com" → Abre en WebView (puede tener restricciones)
- URLs sin "youtube.com" → Reproduce con VideoPlayerDialog (sin restricciones)

## 💾 Límites de Tamaño

**Configurado en `settings.py`:**
- Máximo por archivo: 500 MB
- Formatos recomendados: MP4, MOV, AVI

**Recomendaciones:**
- Videos HD (1080p): ~100-200 MB por 10 min
- Usa compresión H.264/H.265 para reducir tamaño
- Considera usar servicios de streaming para videos muy largos

## 🔧 Cambios Técnicos Realizados

### Backend:
1. **Modelo** (`secciones/models/seccion.py`):
   - Nuevo campo `video_file` para almacenar archivos MP4
   - Se guarda en `media/videos/`

2. **Serializer** (`secciones/serializers/seccion.py`):
   - Nuevo campo `video_url_completa` (SerializerMethodField)
   - Prioriza `video_file` sobre `video_url`
   - Devuelve URL completa con dominio

3. **Settings** (`settings.py`):
   - `FILE_UPLOAD_MAX_MEMORY_SIZE = 500 MB`
   - `DATA_UPLOAD_MAX_MEMORY_SIZE = 500 MB`

4. **Admin** (`secciones/admin.py`):
   - Grupo "Recursos Multimedia" con `video_file` y `video_url`
   - Columna "tiene_video" muestra tipo (MP4 o YouTube)

### Frontend:
No requiere cambios. Ya soporta URLs directas de video en `VideoPlayerDialog`.

## 🎬 Ejemplo de Respuesta API

```json
{
  "id": 1,
  "titulo": "Introducción al curso",
  "contenido": "Bienvenidos...",
  "video_url": null,
  "video_file": "/media/videos/intro.mp4",
  "video_url_completa": "https://cursos-online-api.desarrollo-software.xyz/media/videos/intro.mp4",
  "archivo": null,
  "orden": 1,
  "duracion_minutos": 10,
  "modulo": 1
}
```

La app usa `video_url_completa` para reproducir el video.

## 🛠️ Troubleshooting

### Video no se reproduce en la app
- Verifica que el formato sea MP4 (H.264)
- Verifica que la URL completa funcione en navegador
- Revisa permisos de `MEDIA_ROOT` en el servidor

### Error al subir video grande
- Revisa `FILE_UPLOAD_MAX_MEMORY_SIZE` en settings
- Verifica límites del servidor web (Nginx/Apache)
- Considera dividir videos largos en partes

### Video de YouTube con restricciones
- Cambia a `video_file` subiendo el MP4
- O usa "Abrir" en la app para abrir YouTube directamente

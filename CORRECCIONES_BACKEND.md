# CORRECCIONES REALIZADAS EN EL BACKEND

## Problema Principal

Discrepancia entre los tipos de avisos definidos en el backend y los esperados por el frontend.

## Cambios Realizados

### 1. Modelo Aviso (avisos/models/aviso.py)

**Antes:**

```python
TIPO_CHOICES = [
    ('general', 'General'),
    ('curso', 'Relacionado con curso'),
    ('sistema', 'Sistema'),
    ('promocion', 'Promoción'),
]
tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='general')
```

**Después:**

```python
TIPO_CHOICES = [
    ('aviso', 'Aviso'),
    ('mensaje_sistema', 'Mensaje del Sistema'),
    ('recordatorio', 'Recordatorio'),
    ('urgente', 'Urgente'),
]
tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='aviso')
```

### 2. Serializer Aviso (avisos/serializers/aviso.py)

**Problema:** Frontend envía campo `mensaje` pero el modelo tiene `descripcion`

**Solución:** Agregado campo `mensaje` como SerializerMethodField para lectura y manejo en create/update

```python
class AvisoSerializer(serializers.ModelSerializer):
    mensaje = serializers.SerializerMethodField()  # Para lectura

    def get_mensaje(self, obj):
        """Devuelve descripcion como mensaje para compatibilidad"""
        return obj.descripcion

    def create(self, validated_data):
        # Si viene 'mensaje' en initial_data, usar ese valor para 'descripcion'
        if 'mensaje' in self.initial_data:
            validated_data['descripcion'] = self.initial_data['mensaje']
        return super().create(validated_data)
```

### 3. Migración Creada

**Archivo:** `avisos/migrations/0002_alter_aviso_tipo.py`

Actualiza el campo `tipo` para aceptar los nuevos valores.

## Scripts SQL para Actualizar Datos Existentes

Si tienes avisos existentes en la base de datos con los tipos antiguos, ejecuta:

```sql
-- Actualizar tipos de avisos existentes
UPDATE avisos SET tipo = 'aviso' WHERE tipo = 'general';
UPDATE avisos SET tipo = 'mensaje_sistema' WHERE tipo = 'sistema';
-- Los tipos 'curso' y 'promocion' no tienen equivalente directo,
-- puedes mapearlos según tu necesidad:
UPDATE avisos SET tipo = 'aviso' WHERE tipo IN ('curso', 'promocion');
```

## Configuración CORS

El backend ya tiene configurado CORS para desarrollo:

- `http://localhost:5173`
- `http://127.0.0.1:5173`

## Próximos Pasos

1. **Aplicar migraciones:**

   ```bash
   cd backend_cursos_online
   python manage.py migrate avisos
   ```

2. **Actualizar datos existentes** (si los hay) usando los scripts SQL arriba

3. **Reiniciar el servidor:**

   ```bash
   python manage.py runserver
   ```

4. **Probar el frontend:**
   ```bash
   npm run dev
   ```

## Endpoints Verificados

- ✅ `POST /api/avisos/` - Crear aviso (acepta campo `mensaje`)
- ✅ `GET /api/avisos/` - Listar avisos (devuelve campo `mensaje`)
- ✅ `GET /api/users/?search=` - Buscar usuarios
- ✅ `POST /api/notificaciones/` - Crear notificación

## Componentes Frontend Actualizados

- ✅ `CrearAviso.tsx` - Usa UserSearchDropdown
- ✅ `CrearNotificacion.tsx` - Usa UserSearchDropdown
- ✅ `UserSearchDropdown.tsx` - Soporte para prop `label`
- ✅ `TipoBadge.tsx` - Soporte para tipos: aviso, mensaje_sistema, recordatorio, urgente

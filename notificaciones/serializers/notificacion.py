from rest_framework import serializers
from notificaciones.models import Notificacion
from datetime import datetime
import logging

logger = logging.getLogger('notificaciones')


class NotificacionSerializer(serializers.Serializer):
    """
    Serializer para el modelo Notificacion de MongoDB.
    """
    id = serializers.CharField(read_only=True)
    usuario_id = serializers.IntegerField(required=True)
    tipo = serializers.ChoiceField(
        choices=Notificacion.TIPO_CHOICES,
        required=True
    )
    titulo = serializers.CharField(max_length=200, required=True)
    mensaje = serializers.CharField(required=True)
    leida = serializers.BooleanField(default=False)
    fecha_creacion = serializers.DateTimeField(read_only=True)
    fecha_lectura = serializers.DateTimeField(read_only=True, allow_null=True)
    datos_extra = serializers.DictField(default=dict, required=False)
    
    def create(self, validated_data):
        """Crea una nueva notificación en MongoDB"""
        try:
            logger.info(f"Creando notificación con datos: {validated_data}")
            notificacion = Notificacion(**validated_data)
            notificacion.save()
            logger.info(f"✓ Notificación guardada exitosamente. ID: {notificacion.id}")
            return notificacion
        except Exception as e:
            logger.error(f"✗ Error al crear notificación: {str(e)}")
            raise
    
    def update(self, instance, validated_data):
        """Actualiza una notificación existente"""
        # Solo permitir actualizar ciertos campos
        instance.leida = validated_data.get('leida', instance.leida)
        
        # Si se marca como leída por primera vez, registrar la fecha
        if instance.leida and not instance.fecha_lectura:
            instance.fecha_lectura = datetime.utcnow()
        
        # Actualizar campos opcionales
        if 'titulo' in validated_data:
            instance.titulo = validated_data['titulo']
        if 'mensaje' in validated_data:
            instance.mensaje = validated_data['mensaje']
        if 'datos_extra' in validated_data:
            instance.datos_extra = validated_data['datos_extra']
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        """Convierte el documento de MongoDB a diccionario"""
        return {
            'id': str(instance.id),
            'usuario_id': instance.usuario_id,
            'tipo': instance.tipo,
            'titulo': instance.titulo,
            'mensaje': instance.mensaje,
            'leida': instance.leida,
            'fecha_creacion': instance.fecha_creacion.isoformat() if instance.fecha_creacion else None,
            'fecha_lectura': instance.fecha_lectura.isoformat() if instance.fecha_lectura else None,
            'datos_extra': instance.datos_extra,
        }

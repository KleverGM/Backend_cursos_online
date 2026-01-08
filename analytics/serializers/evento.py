from rest_framework import serializers
from ..models import EventoUsuario


class EventoUsuarioSerializer(serializers.Serializer):
    """Serializer para eventos de usuario"""
    id = serializers.CharField(read_only=True)
    usuario_id = serializers.IntegerField(read_only=True)
    tipo_evento = serializers.CharField(max_length=50)
    fecha_hora = serializers.DateTimeField(read_only=True)
    
    # Campos opcionales
    curso_id = serializers.IntegerField(required=False, allow_null=True)
    seccion_id = serializers.IntegerField(required=False, allow_null=True)
    modulo_id = serializers.IntegerField(required=False, allow_null=True)
    metadata = serializers.DictField(required=False, default=dict)
    
    # Información de sesión (auto-poblado)
    sesion_id = serializers.CharField(read_only=True, required=False)
    ip_address = serializers.CharField(read_only=True, required=False)
    user_agent = serializers.CharField(read_only=True, required=False)
    url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    referrer = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    duracion_segundos = serializers.IntegerField(required=False, default=0)
    
    def validate_tipo_evento(self, value):
        """Validar que el tipo de evento sea válido"""
        tipos_validos = [choice for choice in EventoUsuario.TIPO_EVENTO_CHOICES]
        if value not in tipos_validos:
            raise serializers.ValidationError(
                f"Tipo de evento inválido. Opciones: {', '.join(tipos_validos)}"
            )
        return value
    
    def create(self, validated_data):
        """Crear evento"""
        request = self.context.get('request')
        
        # Asignar usuario_id del usuario autenticado
        if request and request.user.is_authenticated:
            validated_data['usuario_id'] = request.user.id
        
        # Agregar información de sesión automáticamente
        if request:
            validated_data['sesion_id'] = request.session.session_key or ''
            validated_data['ip_address'] = self._get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            if not validated_data.get('url'):
                validated_data['url'] = request.build_absolute_uri()
            if not validated_data.get('referrer'):
                referrer = request.META.get('HTTP_REFERER', '')
                validated_data['referrer'] = referrer if referrer else ''
        
        evento = EventoUsuario(**validated_data)
        evento.save()
        return evento
    
    def _get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def to_representation(self, instance):
        """Convertir documento MongoDB a diccionario"""
        return {
            'id': str(instance.id),
            'usuario_id': instance.usuario_id,
            'tipo_evento': instance.tipo_evento,
            'fecha_hora': instance.fecha_hora.isoformat() if instance.fecha_hora else None,
            'curso_id': instance.curso_id,
            'seccion_id': instance.seccion_id,
            'modulo_id': instance.modulo_id,
            'metadata': instance.metadata,
            'sesion_id': instance.sesion_id,
            'ip_address': instance.ip_address,
            'user_agent': instance.user_agent,
            'url': instance.url,
            'referrer': instance.referrer,
            'duracion_segundos': instance.duracion_segundos,
        }

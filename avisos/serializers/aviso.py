from rest_framework import serializers
from ..models import Aviso
from users.serializers import UsuarioPublicSerializer


class AvisoSerializer(serializers.ModelSerializer):
    usuario = UsuarioPublicSerializer(read_only=True)
    usuario_id = serializers.IntegerField(write_only=True, required=False)
    mensaje = serializers.SerializerMethodField()  # Para lectura, devuelve descripcion
    
    class Meta:
        model = Aviso
        fields = ('id', 'titulo', 'descripcion', 'mensaje', 'tipo', 'fecha_creacion', 
                 'fecha_envio', 'leido', 'comentario', 'usuario', 'usuario_id')
        read_only_fields = ('fecha_creacion', 'usuario')
        extra_kwargs = {
            'descripcion': {'write_only': True, 'required': False}
        }
    
    def get_mensaje(self, obj):
        """Devuelve descripcion como mensaje para compatibilidad con frontend"""
        return obj.descripcion
    
    def create(self, validated_data):
        # Si viene 'mensaje' en initial_data, usar ese valor para 'descripcion'
        if 'mensaje' in self.initial_data:
            validated_data['descripcion'] = self.initial_data['mensaje']
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Si viene 'mensaje' en initial_data, usar ese valor para 'descripcion'
        if 'mensaje' in self.initial_data:
            validated_data['descripcion'] = self.initial_data['mensaje']
        return super().update(instance, validated_data)
from rest_framework import serializers
from ..models import Aviso
from users.serializers import UsuarioPublicSerializer


class AvisoSerializer(serializers.ModelSerializer):
    usuario = UsuarioPublicSerializer(read_only=True)
    usuario_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Aviso
        fields = ('id', 'titulo', 'descripcion', 'tipo', 'fecha_creacion', 
                 'fecha_envio', 'leido', 'comentario', 'usuario', 'usuario_id')
        read_only_fields = ('fecha_creacion', 'usuario')
from rest_framework import serializers
from ..models import Aviso


class AvisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aviso
        fields = ('id', 'titulo', 'descripcion', 'tipo', 'fecha_creacion', 
                 'fecha_envio', 'leido', 'comentario', 'usuario')
        read_only_fields = ('fecha_creacion', 'usuario')
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request:
            validated_data['usuario'] = request.user
        return super().create(validated_data)
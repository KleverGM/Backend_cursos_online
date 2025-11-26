from rest_framework import serializers
from ..models import Seccion, ProgresoSeccion


class SeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seccion
        fields = ('id', 'titulo', 'contenido', 'video_url', 'archivo', 
                 'orden', 'duracion_minutos', 'modulo')


class SeccionDetalladaSerializer(serializers.ModelSerializer):
    """Serializer con información de progreso para usuarios autenticados"""
    progreso_usuario = serializers.SerializerMethodField()
    
    class Meta:
        model = Seccion
        fields = ('id', 'titulo', 'contenido', 'video_url', 'archivo', 
                 'orden', 'duracion_minutos', 'modulo', 'progreso_usuario')
    
    def get_progreso_usuario(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progreso = ProgresoSeccion.objects.get(usuario=request.user, seccion=obj)
                return {
                    'completado': progreso.completado,
                    'tiempo_visto': progreso.tiempo_visto,
                    'fecha_completado': progreso.fecha_completado
                }
            except ProgresoSeccion.DoesNotExist:
                return {
                    'completado': False,
                    'tiempo_visto': 0,
                    'fecha_completado': None
                }
        return None


class ProgresoSeccionSerializer(serializers.ModelSerializer):
    seccion = SeccionSerializer(read_only=True)
    seccion_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ProgresoSeccion
        fields = ('id', 'completado', 'fecha_completado', 'tiempo_visto', 
                 'seccion', 'seccion_id', 'usuario')
        read_only_fields = ('fecha_completado', 'usuario')
    
    def create(self, validated_data):
        from inscripciones.models import Inscripcion
        
        request = self.context.get('request')
        if request:
            validated_data['usuario'] = request.user
        seccion_id = validated_data.pop('seccion_id')
        seccion = Seccion.objects.get(id=seccion_id)
        validated_data['seccion'] = seccion
        
        # Verificar que el usuario esté inscrito en el curso
        if not Inscripcion.objects.filter(
            usuario=request.user, 
            curso=seccion.modulo.curso
        ).exists():
            raise serializers.ValidationError("Debes estar inscrito en el curso para marcar progreso")
        
        return super().create(validated_data)
from rest_framework import serializers
from ..models import Seccion, ProgresoSeccion


class SeccionSerializer(serializers.ModelSerializer):
    archivo = serializers.FileField(required=False, allow_null=True)
    video_file = serializers.FileField(required=False, allow_null=True)
    video_url_completa = serializers.SerializerMethodField()
    
    class Meta:
        model = Seccion
        fields = ('id', 'titulo', 'contenido', 'video_url', 'video_file', 
                 'video_url_completa', 'archivo', 'orden', 'duracion_minutos', 
                 'modulo', 'es_preview')
    
    def get_video_url_completa(self, obj):
        """Devuelve la URL completa del video, ya sea YouTube o archivo subido"""
        request = self.context.get('request')
        
        # Si tiene video_file (MP4 subido), devolver URL completa
        if obj.video_file:
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        
        # Si no, devolver video_url (YouTube)
        return obj.video_url
        
    def validate(self, data):
        # Asegurar que al menos haya contenido, video o archivo
        if not data.get('contenido') and not data.get('video_url') and not data.get('video_file') and not data.get('archivo'):
            raise serializers.ValidationError(
                "La sección debe tener al menos contenido de texto, un video o un archivo"
            )
        return data


class SeccionDetalladaSerializer(serializers.ModelSerializer):
    """Serializer con información de progreso para usuarios autenticados"""
    progreso_usuario = serializers.SerializerMethodField()
    video_url_completa = serializers.SerializerMethodField()
    
    class Meta:
        model = Seccion
        fields = ('id', 'titulo', 'contenido', 'video_url', 'video_file',
                 'video_url_completa', 'archivo', 'orden', 'duracion_minutos', 
                 'modulo', 'progreso_usuario')
    
    def get_video_url_completa(self, obj):
        """Devuelve la URL completa del video, ya sea YouTube o archivo subido"""
        request = self.context.get('request')
        
        # Si tiene video_file (MP4 subido), devolver URL completa
        if obj.video_file:
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        
        # Si no, devolver video_url (YouTube)
        return obj.video_url
    
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
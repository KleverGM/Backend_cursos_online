from rest_framework import serializers
from ..models import Inscripcion
from users.serializers import UsuarioPublicSerializer


class InscripcionSerializer(serializers.ModelSerializer):
    usuario = UsuarioPublicSerializer(read_only=True)
    curso = serializers.SerializerMethodField()
    curso_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Inscripcion
        fields = ('id', 'fecha_inscripcion', 'progreso', 'completado', 
                 'fecha_completado', 'curso', 'usuario', 'curso_id')
        read_only_fields = ('fecha_inscripcion', 'fecha_completado', 'usuario')
    
    def get_curso(self, obj):
        from cursos.serializers import CursoSerializer
        return CursoSerializer(obj.curso).data
    
    def create(self, validated_data):
        from cursos.models import Curso
        
        request = self.context.get('request')
        if request:
            validated_data['usuario'] = request.user
        curso_id = validated_data.pop('curso_id')
        curso = Curso.objects.get(id=curso_id)
        validated_data['curso'] = curso
        return super().create(validated_data)
    
    def validate_curso_id(self, value):
        from cursos.models import Curso
        
        try:
            curso = Curso.objects.get(id=value, activo=True)
            request = self.context.get('request')
            if request and Inscripcion.objects.filter(
                usuario=request.user, 
                curso=curso
            ).exists():
                raise serializers.ValidationError("Ya estás inscrito en este curso")
            return value
        except Curso.DoesNotExist:
            raise serializers.ValidationError("El curso no existe o no está activo")


class InscripcionDetalladaSerializer(serializers.ModelSerializer):
    """Serializer con información detallada del curso y progreso"""
    curso = serializers.SerializerMethodField()
    usuario = UsuarioPublicSerializer(read_only=True)
    progreso_secciones = serializers.SerializerMethodField()
    
    class Meta:
        model = Inscripcion
        fields = ('id', 'fecha_inscripcion', 'progreso', 'completado', 
                 'fecha_completado', 'curso', 'usuario', 'progreso_secciones')
    
    def get_curso(self, obj):
        from cursos.serializers import CursoDetalladoSerializer
        return CursoDetalladoSerializer(obj.curso, context=self.context).data
    
    def get_progreso_secciones(self, obj):
        from secciones.models import ProgresoSeccion
        from secciones.serializers import ProgresoSeccionSerializer
        
        progresos = ProgresoSeccion.objects.filter(
            usuario=obj.usuario,
            seccion__modulo__curso=obj.curso
        )
        return ProgresoSeccionSerializer(progresos, many=True).data
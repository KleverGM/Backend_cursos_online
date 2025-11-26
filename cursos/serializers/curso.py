from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import models
from ..models import Curso
from users.serializers import UsuarioPublicSerializer
from secciones.models import Seccion

User = get_user_model()


class CursoSerializer(serializers.ModelSerializer):
    instructor = UsuarioPublicSerializer(read_only=True, allow_null=True)
    instructor_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    total_modulos = serializers.SerializerMethodField()
    total_secciones = serializers.SerializerMethodField()
    duracion_total = serializers.SerializerMethodField()
    total_estudiantes = serializers.SerializerMethodField()
    
    class Meta:
        model = Curso
        fields = ('id', 'titulo', 'descripcion', 'categoria', 'nivel', 
                 'fecha_creacion', 'instructor', 'instructor_id', 'precio', 'imagen', 'activo',
                 'total_modulos', 'total_secciones', 'duracion_total', 'total_estudiantes')
        read_only_fields = ('fecha_creacion',)
    
    def validate_instructor_id(self, value):
        if value is not None: 
            try:
                instructor = User.objects.get(id=value)
                if instructor.perfil not in ['instructor', 'administrador']:
                    raise serializers.ValidationError("El usuario debe ser instructor o administrador")
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("Usuario no encontrado")
        return value
    
    def get_total_modulos(self, obj):
        return obj.modulos.count()
    
    def get_total_secciones(self, obj):
        return Seccion.objects.filter(modulo__curso=obj).count()
    
    def get_duracion_total(self, obj):
        return Seccion.objects.filter(modulo__curso=obj).aggregate(
            total=models.Sum('duracion_minutos')
        )['total'] or 0
    
    def get_total_estudiantes(self, obj):
        return obj.inscripciones.count()
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request:
            validated_data['instructor'] = request.user
        return super().create(validated_data)


class CursoDetalladoSerializer(serializers.ModelSerializer):
    instructor = UsuarioPublicSerializer(read_only=True)
    modulos = serializers.SerializerMethodField()
    inscripcion_usuario = serializers.SerializerMethodField()
    total_modulos = serializers.SerializerMethodField()
    total_secciones = serializers.SerializerMethodField()
    duracion_total = serializers.SerializerMethodField()
    total_estudiantes = serializers.SerializerMethodField()
    
    class Meta:
        model = Curso
        fields = ('id', 'titulo', 'descripcion', 'categoria', 'nivel', 
                 'fecha_creacion', 'instructor', 'precio', 'imagen', 'activo',
                 'modulos', 'inscripcion_usuario', 'total_modulos', 'total_secciones', 
                 'duracion_total', 'total_estudiantes')
    
    def get_modulos(self, obj):
        from modulos.serializers import ModuloDetalladoSerializer
        return ModuloDetalladoSerializer(obj.modulos.all(), many=True).data
    
    def get_inscripcion_usuario(self, obj):
        from inscripciones.models import Inscripcion
        
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                inscripcion = Inscripcion.objects.get(usuario=request.user, curso=obj)
                return {
                    'inscrito': True,
                    'progreso': inscripcion.progreso,
                    'completado': inscripcion.completado,
                    'fecha_inscripcion': inscripcion.fecha_inscripcion
                }
            except Inscripcion.DoesNotExist:
                return {'inscrito': False}
        return None
    
    def get_total_modulos(self, obj):
        return obj.modulos.count()
    
    def get_total_secciones(self, obj):
        return Seccion.objects.filter(modulo__curso=obj).count()
    
    def get_duracion_total(self, obj):
        return Seccion.objects.filter(modulo__curso=obj).aggregate(
            total=models.Sum('duracion_minutos')
        )['total'] or 0
    
    def get_total_estudiantes(self, obj):
        return obj.inscripciones.count()
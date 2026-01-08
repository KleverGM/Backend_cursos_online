from rest_framework import serializers
from ..models import Inscripcion
from users.serializers import UsuarioPublicSerializer


class InscripcionSerializer(serializers.ModelSerializer):
    usuario = UsuarioPublicSerializer(read_only=True)
    curso = serializers.SerializerMethodField()
    curso_id = serializers.IntegerField(write_only=True, required=False)
    usuario_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Inscripcion
        fields = ('id', 'fecha_inscripcion', 'progreso', 'completado', 
                 'fecha_completado', 'curso', 'usuario', 'curso_id', 'usuario_id')
        read_only_fields = ('fecha_inscripcion', 'fecha_completado', 'usuario')
    
    def get_curso(self, obj):
        from cursos.serializers import CursoSerializer
        return CursoSerializer(obj.curso).data
    
    def create(self, validated_data):
        from cursos.models import Curso
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        request = self.context.get('request')
        
        # Si no se especifica usuario_id, usar el usuario del request
        usuario_id = validated_data.pop('usuario_id', None)
        if usuario_id:
            # Admin especificó un usuario
            try:
                usuario = User.objects.get(id=usuario_id)
                validated_data['usuario'] = usuario
            except User.DoesNotExist:
                raise serializers.ValidationError({"usuario_id": "El usuario especificado no existe"})
        elif request:
            # Usar el usuario del request (estudiante inscribiéndose)
            validated_data['usuario'] = request.user
        else:
            raise serializers.ValidationError({"usuario_id": "Debe especificar un usuario"})
            
        curso_id = validated_data.pop('curso_id')
        try:
            curso = Curso.objects.get(id=curso_id)
            validated_data['curso'] = curso
        except Curso.DoesNotExist:
            raise serializers.ValidationError({"curso_id": "El curso especificado no existe"})
            
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Permitir que admin actualice inscripciones incluyendo cambio de curso"""
        from cursos.models import Curso
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        request = self.context.get('request')
        
        # Si se especifica usuario_id (solo admin puede hacerlo)
        usuario_id = validated_data.pop('usuario_id', None)
        if usuario_id:
            if request and request.user.perfil == 'administrador':
                try:
                    usuario = User.objects.get(id=usuario_id)
                    instance.usuario = usuario
                except User.DoesNotExist:
                    raise serializers.ValidationError({"usuario_id": "El usuario especificado no existe"})
        
        # Si se especifica curso_id
        curso_id = validated_data.pop('curso_id', None)
        if curso_id:
            try:
                curso = Curso.objects.get(id=curso_id)
                instance.curso = curso
            except Curso.DoesNotExist:
                raise serializers.ValidationError({"curso_id": "El curso especificado no existe"})
        
        # Actualizar otros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
    def validate_curso_id(self, value):
        from cursos.models import Curso
        
        try:
            curso = Curso.objects.get(id=value, activo=True)
            request = self.context.get('request')
            
            # Solo validar duplicados si no es una actualización
            if request and not self.instance:
                # Determinar qué usuario se está inscribiendo
                usuario_a_inscribir = request.user
                
                # Si es admin y especificó usuario_id, usar ese usuario
                if request.user.perfil == 'administrador' and 'usuario_id' in self.initial_data:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    usuario_id = self.initial_data.get('usuario_id')
                    try:
                        usuario_a_inscribir = User.objects.get(id=usuario_id)
                    except User.DoesNotExist:
                        raise serializers.ValidationError("El usuario especificado no existe")
                
                # Verificar si ya está inscrito
                if Inscripcion.objects.filter(
                    usuario=usuario_a_inscribir, 
                    curso=curso
                ).exists():
                    raise serializers.ValidationError(
                        f"{'El usuario ya está' if request.user.perfil == 'administrador' else 'Ya estás'} inscrito en este curso"
                    )
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
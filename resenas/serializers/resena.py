from rest_framework import serializers
from ..models import Resena, Respuesta
from inscripciones.models import Inscripcion
from django.contrib.auth import get_user_model

User = get_user_model()


class RespuestaSerializer(serializers.Serializer):
    """Serializer para respuestas anidadas"""
    usuario_id = serializers.IntegerField()
    texto = serializers.CharField(max_length=1000)
    fecha = serializers.DateTimeField(read_only=True)


class ResenaSerializer(serializers.Serializer):
    """Serializer para reseñas de cursos"""
    id = serializers.CharField(read_only=True, source='pk')
    curso_id = serializers.IntegerField()
    usuario_id = serializers.IntegerField(read_only=True)
    rating = serializers.FloatField(min_value=1.0, max_value=5.0)
    titulo = serializers.CharField(max_length=200)
    comentario = serializers.CharField()
    fecha_creacion = serializers.DateTimeField(read_only=True)
    fecha_modificacion = serializers.DateTimeField(read_only=True)
    verificado_compra = serializers.BooleanField(read_only=True)
    util_count = serializers.IntegerField(read_only=True)
    usuarios_util = serializers.ListField(child=serializers.IntegerField(), read_only=True)
    respuestas = RespuestaSerializer(many=True, read_only=True)
    imagenes = serializers.ListField(child=serializers.URLField(), required=False)
    tags = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
    
    # Campos calculados
    nombre_usuario = serializers.SerializerMethodField()
    titulo_curso = serializers.SerializerMethodField()
    es_mia = serializers.SerializerMethodField()
    
    def get_nombre_usuario(self, obj):
        """Obtener nombre del usuario desde PostgreSQL"""
        try:
            user = User.objects.get(id=obj.usuario_id)
            return f"{user.first_name} {user.last_name}".strip() or user.username
        except User.DoesNotExist:
            return "Usuario desconocido"
    
    def get_titulo_curso(self, obj):
        """Obtener título del curso desde PostgreSQL"""
        try:
            from cursos.models import Curso
            curso = Curso.objects.get(id=obj.curso_id)
            return curso.titulo
        except:
            return f"Curso {obj.curso_id}"
    
    def get_es_mia(self, obj):
        """Verificar si la reseña es del usuario actual"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.usuario_id == request.user.id
        return False
    
    def validate(self, data):
        """Validaciones personalizadas"""
        request = self.context.get('request')
        curso_id = data.get('curso_id')
        
        # Solo validar en creación (no en actualización)
        if self.instance is None:
            # Verificar que el usuario esté inscrito
            if not Inscripcion.objects.filter(
                usuario=request.user,
                curso_id=curso_id
            ).exists():
                raise serializers.ValidationError(
                    "Debes estar inscrito en el curso para dejar una reseña"
                )
            
            # Verificar que no sea el instructor de su propio curso
            from cursos.models import Curso
            try:
                curso = Curso.objects.get(id=curso_id)
                if curso.instructor == request.user:
                    raise serializers.ValidationError(
                        "No puedes dejar una reseña en tu propio curso"
                    )
            except Curso.DoesNotExist:
                raise serializers.ValidationError("El curso especificado no existe")
            
            # Verificar que no tenga ya una reseña
            if Resena.objects(usuario_id=request.user.id, curso_id=curso_id).first():
                raise serializers.ValidationError(
                    "Ya tienes una reseña en este curso. Puedes editarla."
                )
        
        return data
    
    def create(self, validated_data):
        """Crear nueva reseña"""
        request = self.context.get('request')
        
        # Verificar si está inscrito para marcar como verificado
        inscrito = Inscripcion.objects.filter(
            usuario=request.user,
            curso_id=validated_data['curso_id']
        ).exists()
        
        resena = Resena(
            usuario_id=request.user.id,
            curso_id=validated_data['curso_id'],
            rating=validated_data['rating'],
            titulo=validated_data['titulo'],
            comentario=validated_data['comentario'],
            verificado_compra=inscrito,
            imagenes=validated_data.get('imagenes', []),
            tags=validated_data.get('tags', [])
        )
        resena.save()
        return resena
        return resena
    
    def update(self, instance, validated_data):
        """Actualizar reseña existente"""
        from datetime import datetime
        
        instance.rating = validated_data.get('rating', instance.rating)
        instance.titulo = validated_data.get('titulo', instance.titulo)
        instance.comentario = validated_data.get('comentario', instance.comentario)
        instance.imagenes = validated_data.get('imagenes', instance.imagenes)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.fecha_modificacion = datetime.utcnow()
        instance.save()
        return instance
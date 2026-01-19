from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)
    tipo_usuario = serializers.CharField(write_only=True, required=False)
    is_active = serializers.BooleanField(required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'perfil', 'is_active', 'fecha_creacion', 'password', 'password_confirm', 'tipo_usuario')
        read_only_fields = ('fecha_creacion',)
    
    def validate_tipo_usuario(self, value):
        """Validar que tipo_usuario sea válido"""
        if value and value not in ['estudiante', 'instructor', 'administrador']:
            raise serializers.ValidationError("tipo_usuario debe ser: estudiante, instructor o administrador")
        return value
    
    def validate(self, attrs):
        # Al crear, la contraseña es obligatoria
        if self.instance is None and 'password' not in attrs:
            raise serializers.ValidationError({"password": "La contraseña es requerida al crear un usuario"})
        
        # Solo validar password_confirm si está presente
        if 'password_confirm' in attrs:
            if attrs.get('password') != attrs.get('password_confirm'):
                raise serializers.ValidationError("Las contraseñas no coinciden")
        return attrs
    
    def create(self, validated_data):
        # Mapear tipo_usuario a perfil
        if 'tipo_usuario' in validated_data:
            validated_data['perfil'] = validated_data.pop('tipo_usuario')
        
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        # Mapear tipo_usuario a perfil si está presente
        if 'tipo_usuario' in validated_data:
            validated_data['perfil'] = validated_data.pop('tipo_usuario')
        
        # Remover password_confirm si está presente
        validated_data.pop('password_confirm', None)
        
        # Si hay password, actualizarlo aparte
        password = validated_data.pop('password', None)
        
        # Actualizar campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Si hay password, establecerla
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UsuarioPublicSerializer(serializers.ModelSerializer):
    """Serializer público para mostrar información básica del usuario"""
    tipo_usuario = serializers.CharField(source='perfil', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'tipo_usuario', 'email')


class UsuarioResponseSerializer(serializers.ModelSerializer):
    """Serializer para respuestas de login/registro"""
    tipo_usuario = serializers.CharField(source='perfil', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'fecha_creacion')


class EstadisticasUsuarioSerializer(serializers.Serializer):
    """Serializer para estadísticas del usuario"""
    total_cursos_inscritos = serializers.IntegerField()
    cursos_completados = serializers.IntegerField()
    progreso_promedio = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_tiempo_estudiado = serializers.IntegerField()  # en minutos
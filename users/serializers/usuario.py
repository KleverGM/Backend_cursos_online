from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)
    tipo_usuario = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'perfil', 'tipo_usuario', 'fecha_creacion', 'password', 'password_confirm', 'is_active')
        read_only_fields = ('fecha_creacion', 'tipo_usuario')
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'perfil': {'required': False},
        }
    
    def get_tipo_usuario(self, obj):
        """Retornar el perfil como tipo_usuario"""
        return obj.perfil
    
    def validate_perfil(self, value):
        """Validar que perfil sea válido"""
        if value and value not in ['estudiante', 'instructor', 'administrador']:
            raise serializers.ValidationError("perfil debe ser: estudiante, instructor o administrador")
        return value
    
    def validate(self, attrs):
        # Solo validar password_confirm si está presente
        if 'password_confirm' in attrs:
            if attrs.get('password') != attrs.get('password_confirm'):
                raise serializers.ValidationError("Las contraseñas no coinciden")
        
        # En creación, password es obligatorio
        if not self.instance and 'password' not in attrs:
            raise serializers.ValidationError("password es requerido al crear un usuario")
        
        return attrs
    
    def create(self, validated_data):
        # Validar que password esté presente
        if 'password' not in validated_data:
            raise serializers.ValidationError("password es requerido")
        
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        # Remover campos que no se deben actualizar aquí
        validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        # Validar unicidad de email si se está actualizando
        if 'email' in validated_data:
            email = validated_data['email']
            if User.objects.exclude(pk=instance.pk).filter(email=email).exists():
                raise serializers.ValidationError({'email': 'Este email ya está en uso'})
        
        # Validar unicidad de username si se está actualizando
        if 'username' in validated_data:
            username = validated_data['username']
            if User.objects.exclude(pk=instance.pk).filter(username=username).exists():
                raise serializers.ValidationError({'username': 'Este username ya está en uso'})
        
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class UsuarioPublicSerializer(serializers.ModelSerializer):
    """Serializer público para mostrar información básica del usuario"""
    tipo_usuario = serializers.CharField(source='perfil', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'tipo_usuario', 'perfil', 'email')


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
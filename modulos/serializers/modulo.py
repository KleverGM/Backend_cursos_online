from rest_framework import serializers
from django.db import models
from ..models import Modulo


class ModuloSerializer(serializers.ModelSerializer):
    total_secciones = serializers.SerializerMethodField()
    duracion_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Modulo
        fields = ('id', 'titulo', 'descripcion', 'orden', 'curso', 
                 'total_secciones', 'duracion_total')
    
    def get_total_secciones(self, obj):
        return obj.secciones.count()
    
    def get_duracion_total(self, obj):
        return obj.secciones.aggregate(
            total=models.Sum('duracion_minutos')
        )['total'] or 0


class ModuloDetalladoSerializer(serializers.ModelSerializer):
    secciones = serializers.SerializerMethodField()
    total_secciones = serializers.SerializerMethodField()
    duracion_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Modulo
        fields = ('id', 'titulo', 'descripcion', 'orden', 'curso', 
                 'secciones', 'total_secciones', 'duracion_total')
    
    def get_secciones(self, obj):
        from secciones.serializers import SeccionSerializer
        return SeccionSerializer(obj.secciones.all(), many=True).data
    
    def get_total_secciones(self, obj):
        return obj.secciones.count()
    
    def get_duracion_total(self, obj):
        return obj.secciones.aggregate(
            total=models.Sum('duracion_minutos')
        )['total'] or 0
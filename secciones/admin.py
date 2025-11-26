from django.contrib import admin
from .models import Seccion, ProgresoSeccion


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'modulo', 'orden', 'duracion_minutos')
    list_filter = ('modulo__curso',)
    search_fields = ('titulo', 'modulo__titulo', 'contenido')
    ordering = ('modulo', 'orden')


@admin.register(ProgresoSeccion)
class ProgresoSeccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'seccion', 'completado', 'tiempo_visto', 'fecha_completado')
    list_filter = ('completado', 'fecha_completado')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'seccion__titulo')
    readonly_fields = ('fecha_completado',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'seccion')

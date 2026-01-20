from django.contrib import admin
from .models import Seccion, ProgresoSeccion


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'modulo', 'orden', 'duracion_minutos', 'tiene_video')
    list_filter = ('modulo__curso',)
    search_fields = ('titulo', 'modulo__titulo', 'contenido')
    ordering = ('modulo', 'orden')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'modulo', 'orden', 'duracion_minutos')
        }),
        ('Contenido', {
            'fields': ('contenido',)
        }),
        ('Recursos Multimedia', {
            'fields': ('video_file', 'video_url', 'archivo'),
            'description': '💡 Sube un archivo MP4 usando "video_file" (sin restricciones) o pega una URL de YouTube en "video_url"'
        }),
    )
    
    def tiene_video(self, obj):
        """Mostrar icono si la sección tiene video"""
        if obj.video_file:
            return '📁 Video MP4'
        elif obj.video_url:
            return '🎬 YouTube'
        return '-'
    tiene_video.short_description = 'Video'


@admin.register(ProgresoSeccion)
class ProgresoSeccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'seccion', 'completado', 'tiempo_visto', 'fecha_completado')
    list_filter = ('completado', 'fecha_completado')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'seccion__titulo')
    readonly_fields = ('fecha_completado',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'seccion')

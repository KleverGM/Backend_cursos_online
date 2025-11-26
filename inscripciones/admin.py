from django.contrib import admin
from .models import Inscripcion


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'curso', 'progreso', 'completado', 'fecha_inscripcion')
    list_filter = ('completado', 'fecha_inscripcion', 'curso')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'curso__titulo')
    ordering = ('-fecha_inscripcion',)
    readonly_fields = ('fecha_completado',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'curso')

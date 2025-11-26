from django.contrib import admin
from .models import Curso


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'instructor', 'categoria', 'nivel', 'precio', 'activo', 'fecha_creacion')
    list_filter = ('categoria', 'nivel', 'activo', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion', 'instructor__first_name', 'instructor__last_name')
    ordering = ('-fecha_creacion',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('instructor')

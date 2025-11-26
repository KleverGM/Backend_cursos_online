from django.contrib import admin
from .models import Aviso


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'leido', 'fecha_creacion', 'fecha_envio')
    list_filter = ('tipo', 'leido', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion', 'usuario__first_name', 'usuario__last_name')
    ordering = ('-fecha_creacion',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')

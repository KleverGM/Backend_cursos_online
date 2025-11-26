from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'perfil', 'is_active', 'fecha_creacion')
    list_filter = ('perfil', 'is_active', 'is_staff', 'fecha_creacion')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-fecha_creacion',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('perfil', 'fecha_creacion')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('email', 'first_name', 'last_name', 'perfil')
        }),
    )
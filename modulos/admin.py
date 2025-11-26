from django.contrib import admin
from .models import Modulo


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso', 'orden')
    list_filter = ('curso',)
    search_fields = ('titulo', 'curso__titulo')
    ordering = ('curso', 'orden')

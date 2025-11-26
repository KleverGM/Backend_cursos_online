from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado que permite al propietario o administrador acceder
    """
    def has_object_permission(self, request, view, obj):
        # Lectura para cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
            
        # Escritura para propietario del curso/módulo o admin
        if hasattr(obj, 'modulo') and hasattr(obj.modulo, 'curso'):
            curso = obj.modulo.curso
            if hasattr(curso, 'instructor'):
                return curso.instructor == request.user or request.user.perfil == 'administrador'
        elif hasattr(obj, 'usuario'):
            return obj.usuario == request.user or request.user.perfil == 'administrador'
        return request.user.perfil == 'administrador'


class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Permiso que solo permite acceso a instructores y administradores
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.perfil in ['instructor', 'administrador']
        )
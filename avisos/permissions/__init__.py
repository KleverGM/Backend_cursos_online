from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado que permite al propietario o administrador acceder
    """
    def has_object_permission(self, request, view, obj):
        # Lectura para el propietario del aviso o admin
        if request.method in permissions.SAFE_METHODS:
            return obj.usuario == request.user or request.user.perfil == 'administrador'
            
        # Escritura para el propietario del aviso o admin
        return obj.usuario == request.user or request.user.perfil == 'administrador'


class IsAdminUser(permissions.BasePermission):
    """
    Permiso que solo permite acceso a administradores
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.perfil == 'administrador'
from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado que permite al propietario o administrador acceder al objeto
    """
    def has_object_permission(self, request, view, obj):
        # El propietario del objeto o administrador puede acceder
        return obj == request.user or request.user.perfil == 'administrador'


class IsAdminUser(permissions.BasePermission):
    """
    Permiso que solo permite acceso a administradores
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.perfil == 'administrador'


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


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Permite lectura a cualquier usuario, pero escritura solo al propietario o admin
    """
    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
            
        # Permisos de escritura solo para el propietario o admin
        return obj == request.user or request.user.perfil == 'administrador'
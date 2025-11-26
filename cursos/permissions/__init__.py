from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que solo permite a administradores
    editar/eliminar, pero permite lectura a cualquier usuario autenticado
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.perfil == 'administrador'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado que permite a los propietarios del objeto 
    o administradores realizar operaciones
    """
    def has_object_permission(self, request, view, obj):
        # Permisos de lectura para cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
            
        # Permisos de escritura solo para el propietario o admin
        if hasattr(obj, 'instructor'):
            return obj.instructor == request.user or request.user.perfil == 'administrador'
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
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.perfil == 'administrador'


class IsOwnerOrAdmin(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        if hasattr(obj, 'instructor'):
            return obj.instructor == request.user or request.user.perfil == 'administrador'
        elif hasattr(obj, 'usuario'):
            return obj.usuario == request.user or request.user.perfil == 'administrador'
        return request.user.perfil == 'administrador'


class IsInstructorOrAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.perfil in ['instructor', 'administrador']
        )
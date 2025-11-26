from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
   
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.usuario == request.user or request.user.perfil == 'administrador'
            
        return obj.usuario == request.user or request.user.perfil == 'administrador'


class IsAdminUser(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.perfil == 'administrador'
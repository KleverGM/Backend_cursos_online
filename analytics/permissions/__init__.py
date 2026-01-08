from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Solo administradores pueden acceder"""
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.perfil == 'administrador'
        )

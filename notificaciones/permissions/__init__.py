from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Permiso personalizado para permitir solo al propietario de la notificación o al admin.
    """
    def has_object_permission(self, request, view, obj):
        # Admin puede hacer todo
        if hasattr(request.user, 'rol') and request.user.rol == 'Administrador':
            return True
        
        # El usuario solo puede acceder a sus propias notificaciones
        return obj.usuario_id == request.user.id


class IsAdminUser(BasePermission):
    """
    Permiso para verificar que el usuario es administrador.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'rol') and 
            request.user.rol == 'Administrador'
        )

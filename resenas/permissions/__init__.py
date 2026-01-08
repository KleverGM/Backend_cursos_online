from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado: solo el autor puede editar/eliminar su reseña
    """
    def has_object_permission(self, request, view, obj):
        # Lectura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para el autor
        return obj.usuario_id == request.user.id


class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Permiso para que instructores puedan responder reseñas
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_authenticated and request.user.perfil in ['instructor', 'administrador']
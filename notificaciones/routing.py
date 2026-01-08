from django.urls import path
from notificaciones.consumers import NotificacionConsumer

websocket_urlpatterns = [
    path('ws/notificaciones/', NotificacionConsumer.as_asgi()),
]

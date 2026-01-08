from mongoengine import Document, fields
from datetime import datetime


class EventoUsuario(Document):
    """
    Modelo para rastrear eventos de usuarios en MongoDB
    Almacena acciones como: vistas de página, clics, inicio de video, etc.
    """
    TIPO_EVENTO_CHOICES = [
        'page_view',          # Vista de página
        'curso_view',         # Vista de curso
        'seccion_view',       # Vista de sección
        'video_start',        # Inicio de video
        'video_complete',     # Video completado
        'curso_inscripcion',  # Inscripción a curso
        'resena_create',      # Creación de reseña
        'search',             # Búsqueda
        'click',              # Clic en elemento
        'download',           # Descarga de archivo
        'login',              # Inicio de sesión
        'logout',             # Cierre de sesión
    ]
    
    # Identificación del usuario
    usuario_id = fields.IntField(required=True)
    
    # Tipo de evento
    tipo_evento = fields.StringField(
        required=True,
        choices=TIPO_EVENTO_CHOICES,
        max_length=50
    )
    
    # Fecha y hora del evento
    fecha_hora = fields.DateTimeField(default=datetime.utcnow, required=True)
    
    # Información adicional del evento
    curso_id = fields.IntField()
    seccion_id = fields.IntField()
    modulo_id = fields.IntField()
    
    # Metadata adicional (JSON flexible)
    metadata = fields.DictField(default=dict)
    
    # Información de sesión
    sesion_id = fields.StringField(max_length=100)
    ip_address = fields.StringField(max_length=45)
    user_agent = fields.StringField(max_length=500)
    
    # Información de navegación
    url = fields.StringField(max_length=500)
    referrer = fields.StringField(max_length=500)
    
    # Tiempo dedicado (en segundos)
    duracion_segundos = fields.IntField(default=0)
    
    meta = {
        'collection': 'eventos_usuario',
        'indexes': [
            'usuario_id',
            'tipo_evento',
            'fecha_hora',
            ('usuario_id', 'tipo_evento'),
            ('usuario_id', 'curso_id'),
            '-fecha_hora',  # Índice descendente para consultas recientes
        ],
        'ordering': ['-fecha_hora']
    }
    
    def __str__(self):
        return f"{self.tipo_evento} - Usuario {self.usuario_id} - {self.fecha_hora}"

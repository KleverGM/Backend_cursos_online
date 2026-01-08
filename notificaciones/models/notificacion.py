from mongoengine import Document, fields
from datetime import datetime


class Notificacion(Document):
    """
    Modelo de Notificación almacenado en MongoDB.
    Registra todas las notificaciones enviadas a los usuarios del sistema.
    """
    
    # Tipos de notificaciones disponibles
    TIPO_CHOICES = [
        'nueva_inscripcion',      # Instructor: nuevo estudiante inscrito en tu curso
        'curso_completado',       # Instructor: estudiante completó tu curso
        'nueva_resena',           # Instructor: nueva reseña en tu curso
        'respuesta_resena',       # Estudiante: instructor respondió tu reseña
        'aviso_nuevo',            # Usuario: nuevo aviso importante
        'curso_actualizado',      # Estudiante: curso en el que estás inscrito se actualizó
        'mensaje_sistema',        # Admin: mensaje del sistema
    ]
    
    # Información del destinatario
    usuario_id = fields.IntField(required=True, db_field='usuario_id')
    
    # Información de la notificación
    tipo = fields.StringField(required=True, choices=TIPO_CHOICES, db_field='tipo')
    titulo = fields.StringField(required=True, max_length=200, db_field='titulo')
    mensaje = fields.StringField(required=True, db_field='mensaje')
    
    # Estado de la notificación
    leida = fields.BooleanField(default=False, db_field='leida')
    
    # Fechas
    fecha_creacion = fields.DateTimeField(default=datetime.utcnow, db_field='fecha_creacion')
    fecha_lectura = fields.DateTimeField(null=True, db_field='fecha_lectura')
    
    # Datos adicionales (IDs relacionados, URLs, etc.)
    datos_extra = fields.DictField(default=dict, db_field='datos_extra')
    
    # Metadata de MongoDB
    meta = {
        'collection': 'notificaciones',
        'indexes': [
            'usuario_id',
            'tipo',
            'leida',
            '-fecha_creacion',  # Índice descendente para ordenar por más reciente
            {
                'fields': ['usuario_id', 'leida'],
                'name': 'usuario_leida_idx'
            }
        ],
        'ordering': ['-fecha_creacion']
    }
    
    def __str__(self):
        return f"Notificación {self.tipo} para usuario {self.usuario_id}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = datetime.utcnow()
            self.save()

from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime


class Respuesta(EmbeddedDocument):
    """Respuesta a una reseña (anidada)"""
    usuario_id = fields.IntField(required=True)
    texto = fields.StringField(required=True, max_length=1000)
    fecha = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'strict': False
    }


class Resena(Document):
    """Reseña de un curso en MongoDB"""
    # Referencias a PostgreSQL
    curso_id = fields.IntField(required=True)
    usuario_id = fields.IntField(required=True)
    
    # Contenido de la reseña
    rating = fields.FloatField(required=True, min_value=1.0, max_value=5.0)
    titulo = fields.StringField(required=True, max_length=200)
    comentario = fields.StringField(required=True)
    
    # Timestamps
    fecha_creacion = fields.DateTimeField(default=datetime.utcnow)
    fecha_modificacion = fields.DateTimeField()
    
    # Validación
    verificado_compra = fields.BooleanField(default=False)
    
    # Interacciones
    util_count = fields.IntField(default=0)
    usuarios_util = fields.ListField(fields.IntField())
    
    # Respuestas anidadas
    respuestas = fields.ListField(fields.EmbeddedDocumentField(Respuesta))
    
    # Opcionales
    imagenes = fields.ListField(fields.URLField())
    tags = fields.ListField(fields.StringField(max_length=50))
    
    meta = {
        'collection': 'resenas',
        'indexes': [
            'curso_id',
            'usuario_id',
            '-fecha_creacion',
            'rating',
            {
                'fields': ['usuario_id', 'curso_id'],
                'unique': True  # Una reseña por usuario por curso
            }
        ]
    }
    
    def __str__(self):
        return f"Reseña de usuario {self.usuario_id} en curso {self.curso_id}"
    
    def clean(self):
        """Validación adicional antes de guardar"""
        if self.rating < 1.0 or self.rating > 5.0:
            raise ValueError("El rating debe estar entre 1.0 y 5.0")

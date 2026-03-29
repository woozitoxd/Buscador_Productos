from . import db
from datetime import datetime, timezone

class HistorialBusqueda(db.Model):
    # Definimos explícitamente el nombre de la tabla
    __tablename__ = 'historial_busquedas'
    
    # Definición de las columnas (nuestra Primary Key y los campos de datos)
    id = db.Column(db.Integer, primary_key=True)
    termino = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Busqueda: {self.termino}>'
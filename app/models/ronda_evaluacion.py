import datetime
from app.extension import db

# ------------------------
# Modelo para Rondas del Método Delphi
# ------------------------

class RondaEvaluacion(db.Model):
    __tablename__ = 'rondas_evaluacion'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)  # Número de la ronda
    aplicacion_id = db.Column(db.Integer, db.ForeignKey('aplicaciones.id'), nullable=False)
    fecha_limite = db.Column(db.DateTime, nullable=True)  # Fecha límite para la ronda
    fecha_creacion = db.Column(db.DateTime, default=datetime.timezone.utc)

    # Una ronda puede tener múltiples resultados
    resultados = db.relationship('ResultadoEvaluacion', backref='ronda', lazy=True)

    def __repr__(self):
        return f'<Ronda {self.numero} - Aplicacion {self.aplicacion_id}>'

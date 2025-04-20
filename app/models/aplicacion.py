import datetime
from app.extension import db

# ------------------------
# Modelo de Aplicaciones
# ------------------------
class Aplicacion(db.Model):
    __tablename__ = 'aplicaciones'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)  # Nombre de la aplicación
    descripcion = db.Column(db.Text, nullable=True)     # Descripción detallada
    fecha_creacion = db.Column(db.DateTime, default=datetime.timezone.utc)

    # Relación uno-a-muchos: una aplicación puede tener muchas evaluaciones
    evaluaciones = db.relationship('ResultadoEvaluacion', backref='aplicacion', lazy=True)
    rondas = db.relationship('RondaEvaluacion', backref='aplicacion', lazy=True)

    def __repr__(self):
        return f'<Aplicacion {self.nombre}>'

    def guardar(self):
        db.session.add(self)
        db.session.commit()

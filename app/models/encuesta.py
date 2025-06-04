from app.extension import db

# ------------------------
# Modelo de Encuestas
# ------------------------

class Encuesta(db.Model):
    __tablename__ = 'encuestas'

    id = db.Column(db.Integer, primary_key=True)
    pregunta = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_modificacion = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    # Relación con el modelo de Parámetros de Evaluación (1 encuesta tiene un parámetro de evaluación asociado)
    
    def __init__(self, pregunta):
        self.pregunta = pregunta
    
    def __repr__(self):
        return f'<Encuesta {self.id}: {self.pregunta}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'pregunta': self.pregunta,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'fecha_modificacion': self.fecha_modificacion.isoformat()
        }
        
    def guardar(self):
        db.session.add(self)
        db.session.commit()
    
    def actualizar(self):
        db.session.commit()
    
    def eliminar(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def obtener_por_id(encuesta_id):
        return Encuesta.query.get(encuesta_id)
    
    @staticmethod
    def obtener_todas():
        return Encuesta.query.all()
        
    @staticmethod
    def obtener_por_fecha(fecha_inicio, fecha_fin):
        return Encuesta.query.filter(Encuesta.fecha_creacion.between(fecha_inicio, fecha_fin)).all()
    
    @staticmethod
    def obtener_por_pregunta(pregunta):
        return Encuesta.query.filter(Encuesta.pregunta.ilike(f'%{pregunta}%')).all()
    
        return Encuesta.query.filter(
            Encuesta.id == encuesta_id,
            Encuesta.id_parametro_evaluacion == parametro_id
        ).first()
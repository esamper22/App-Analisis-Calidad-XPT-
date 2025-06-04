from app.extension import db

# ------------------------
# Modelo de Parametro de Evaluación
# ------------------------
class Encuesta(db.Model):
    __tablename__ = 'encuesta'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)  # Nombre del parámetro
    descripcion = db.Column(db.Text, nullable=True)     # Descripción del parámetro
    # tipo = db.Column(db.String(50), nullable=False)     # Tipo de dato (e.g., 'numerico', 'texto', 'booleano')
    
    pesos = db.Column(db.String(50), nullable=True, default='2.0,3.0,4.0,5.0')  # Pesos mínimo y máximo como cadena 'min,max'
    
    # tipos estados separados por comas
    # 'mal', 'regular', 'bien', 'excelente'
    estados = db.Column(db.String(255), nullable=True, default='mal,regular,bien,excelente')  # Estados posibles del parámetro
    
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_modificacion = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, nombre, descripcion=None, pesos=None, estados=None):
        self.nombre = nombre
        # self.tipo = tipo
        self.descripcion = descripcion
        self.pesos = pesos if pesos else '2.0,3.0,4.0,5.0'  # Pesos por defecto
        self.estados = 'mal,regular,bien,excelente' if not estados else estados  # Estados por defecto

    def __repr__(self):
        return f'<ParametroEvaluacion {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            # 'tipo': self.tipo,
            'pesos': [float(peso) for peso in self.pesos.split(',')] if self.pesos else [],
            # Convertir pesos a lista de flotantes
            'estados': self.estados.split(',') if self.estados else [],  # Convertir estados a lista
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
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
    def obtener_por_id(parametro_id):
        return Encuesta.query.get(parametro_id)

    @staticmethod
    def obtener_todos():
        return Encuesta.query.all()

    @staticmethod
    def obtener_por_nombre(nombre):
        return Encuesta.query.filter_by(nombre=nombre).first()

    @staticmethod
    def obtener_por_fecha(fecha_inicio, fecha_fin):
        return Encuesta.query.filter(Encuesta.fecha_creacion.between(fecha_inicio, fecha_fin)).all()


from app.extension import db
import datetime


# ------------------------
# Modelo de Parametro de Evaluación
# ------------------------
class ParametroEvaluacion(db.Model):
    __tablename__ = 'parametros_evaluacion'

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
        return ParametroEvaluacion.query.get(parametro_id)

    @staticmethod
    def obtener_todos():
        return ParametroEvaluacion.query.all()

    @staticmethod
    def obtener_por_nombre(nombre):
        return ParametroEvaluacion.query.filter_by(nombre=nombre).first()

    @staticmethod
    def obtener_por_fecha(fecha_inicio, fecha_fin):
        return ParametroEvaluacion.query.filter(ParametroEvaluacion.fecha_creacion.between(fecha_inicio, fecha_fin)).all()



# ------------------------
# Asociación entre Encuesta y ParametroEvaluacion
# ------------------------
class EncuestaParametro(db.Model):
    __tablename__ = 'encuesta_parametro'

    id = db.Column(db.Integer, primary_key=True)
    parametro_id = db.Column(db.Integer, db.ForeignKey('parametros_evaluacion.id'), nullable=False)
    aplicacion_id = db.Column(db.Integer, db.ForeignKey('aplicaciones.id'), nullable=True)
    # Estado de envio
    estado = db.Column(db.String(50), nullable=True, default='pendiente')  # 'pendiente', 'enviado', 'recibido'

    # Relaciones
    parametro = db.relationship('ParametroEvaluacion', backref='encuesta_parametros')
    aplicacion = db.relationship('Aplicacion', backref='encuesta_parametros')

    def __init__(self, parametro_id, aplicacion_id=None, estado='pendiente'):
        self.parametro_id = parametro_id
        self.aplicacion_id = aplicacion_id
        self.estado = estado

    def __repr__(self):
        return f'<EncuestaParametro Encuesta:{self.encuesta_id} Parametro:{self.parametro_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'encuesta_id': self.encuesta_id,
            'parametro_id': self.parametro_id,
            'aplicacion_id': self.aplicacion_id,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }


# ------------------------
# Modelo de Resultados de Evaluación por Ronda
# ------------------------
class ResultadoEvaluacion(db.Model):
    __tablename__ = 'resultados_evaluacion'

    id = db.Column(db.Integer, primary_key=True)
    aplicacion_id = db.Column(db.Integer, db.ForeignKey('aplicaciones.id'), nullable=False)
    evaluador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ronda_id = db.Column(db.Integer, db.ForeignKey('rondas_evaluacion.id'), nullable=False)

    # Métricas estadísticas calculadas tras cada ronda
    puntuacion_media = db.Column(db.Float, nullable=False)
    desviacion_estandar = db.Column(db.Float, nullable=False)
    puntuacion_minima = db.Column(db.Float, nullable=False)
    puntuacion_maxima = db.Column(db.Float, nullable=False)
    rango_puntuacion = db.Column(db.Float, nullable=False)
    puntuacion_mediana = db.Column(db.Float, nullable=False)
    puntuacion_moda = db.Column(db.Float, nullable=True)

    # Justificación del evaluador (opcional pero útil para análisis cualitativos)
    justificacion = db.Column(db.Text, nullable=True)

    fecha_envio = db.Column(db.DateTime, default=datetime.timezone.utc)

    def __repr__(self):
        return f'<ResultadoEvaluacion App:{self.aplicacion_id} Ronda:{self.ronda_id} Eval:{self.evaluador_id}>'

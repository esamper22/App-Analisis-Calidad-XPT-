from app.extension import db
import datetime


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




# ------------------------
# Modelo Evaluación (n-a-1 con Aplicación)
# ------------------------
class Evaluacion(db.Model):
    __tablename__ = 'evaluaciones'

    id = db.Column(db.Integer, primary_key=True)
    aplicacion_id = db.Column(db.Integer, db.ForeignKey('aplicaciones.id'), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default='pendiente')  # 'pendiente', 'en progreso', 'completada'
    rondas = db.Column(db.Integer, nullable=False, default=3)  # Número de rondas de evaluación
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    comentarios = db.Column(db.Text, nullable=True)

    # Relación n-a-1 con Aplicación
    aplicacion = db.relationship('Aplicacion', backref='evaluaciones_rel')

    # Relaciones n-a-n (se definen abajo con secondary)
    parametros = db.relationship(
        'Encuesta',
        secondary='evaluacion_parametro',  # tabla intermedia
        backref='evaluaciones_parametros'
    )
    usuarios = db.relationship(
        'Usuario',
        secondary='evaluacion_usuario',  # otra tabla intermedia
        backref='evaluaciones_usuarios'
    )

    def __init__(self, aplicacion_id, fecha_inicio, fecha_fin=None, estado='pendiente', comentarios=None, rondas=3):
        self.aplicacion_id = aplicacion_id
        self.estado = estado
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin if fecha_fin else fecha_inicio + datetime.timedelta(days=30)
        self.comentarios = comentarios
        self.rondas = rondas

    def to_dict(self):
        return {
            'id': self.id,
            'aplicacion_id': self.aplicacion_id,
            'estado': self.estado,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'rondas': self.rondas,
            'comentarios': self.comentarios,
            'parametros': [p.to_dict() for p in self.parametros],
            'usuarios':   [u.to_dict() for u in self.usuarios],
        }
    
    @staticmethod
    def obtener_por_id(encuesta_parametro_id):
        return Evaluacion.query.get(encuesta_parametro_id)
    
    @staticmethod
    def obtener_todos():
        return Evaluacion.query.all()
    
    @staticmethod
    def obtener_por_aplicacion(aplicacion_id):
        return Evaluacion.query.filter_by(aplicacion_id=aplicacion_id).all()
    
    @staticmethod
    def obtener_por_aplicacion_y_estado(aplicacion_id, estado):
        return Evaluacion.query.filter_by(aplicacion_id=aplicacion_id, estado=estado).all()
    
    @staticmethod
    def obtener_por_parametro(parametro_id):
        return Evaluacion.query.filter_by(parametro_id=parametro_id).all()
    
    @staticmethod
    def obtener_por_estado(estado):
        return Evaluacion.query.filter_by(estado=estado).all()

    @staticmethod
    def obtener_usuario_notificados(usuario_id):
        """
        Obtiene todas las evaluaciones en las que un usuario ha sido notificado.
        """
        return Evaluacion.query.join(EvaluacionUsuario).filter(EvaluacionUsuario.usuario_id == usuario_id).all()

# ------------------------
# Tabla intermedia Evaluación <-> Parámetro (n-a-n)
# ------------------------
class EvaluacionParametro(db.Model):
    __tablename__ = 'evaluacion_parametro'

    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluaciones.id'), primary_key=True)
    encuesta_id  = db.Column(db.Integer, db.ForeignKey('encuesta.id'), primary_key=True)

# ------------------------
# Tabla intermedia Evaluación <-> Usuario (n-a-n)
# ------------------------
class EvaluacionUsuario(db.Model):
    __tablename__ = 'evaluacion_usuario'

    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluaciones.id'), primary_key=True)
    usuario_id    = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    
    

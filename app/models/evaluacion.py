from app.extension import db
import datetime


# ------------------------
# Modelo Evaluación (n-a-1 con Aplicación)
# ------------------------
class Evaluacion(db.Model):
    __tablename__ = 'evaluaciones'

    id = db.Column(db.Integer, primary_key=True)
    aplicacion_id = db.Column(db.Integer, db.ForeignKey('aplicaciones.id'), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default='pendiente')  # 'pendiente', 'en progreso', 'completada'
    enviada = db.Column(db.Boolean, nullable=False, default=False)
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
            'enviada': self.enviada,
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
    def obtener_evaluaciones_notificados(usuario_id):
        """
        Obtiene todas las aplicaciones en las que un usuario ha sido notificado y la evaluacion haya sido enviada        
        """
        return Evaluacion.query.join(EvaluacionUsuario, Evaluacion.id == EvaluacionUsuario.evaluacion_id) \
            .filter(
            EvaluacionUsuario.usuario_id == usuario_id,
            Evaluacion.estado == 'pendiente'
            ).all()

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
    
    

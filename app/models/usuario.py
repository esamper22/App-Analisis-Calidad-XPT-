import datetime
from .rol import Rol
from app.extension import db
from flask_login import UserMixin

# ------------------------
# Modelo de Usuarios (Evaluadores, Admins, etc.)
# ------------------------
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), unique=True, nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum(Rol), default=Rol.USUARIO)  # Usando el Enum de roles
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now())

    # Relaciones
    evaluaciones = db.relationship('ResultadoEvaluacion', backref='evaluador', lazy=True)
    asociaciones_ronda = db.relationship(
        'ParticipanteRonda',
        back_populates='usuario',
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'

    def guardar(self):
        db.session.add(self)
        db.session.commit()

    # Método para verificar roles
    def tiene_rol(self, rol: Rol):
        return self.rol == rol

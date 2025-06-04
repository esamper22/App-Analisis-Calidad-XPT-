import datetime

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadData, SignatureExpired
from flask_login import UserMixin

from app.extension import db
from .rol import Rol

# ------------------------
# Modelo de Usuarios (Evaluadores, Admins, etc.)
# ------------------------
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    nombre_usuario = db.Column(db.String(100), unique=True, nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column('contrasena_hash', db.String(255), nullable=False)
    rol = db.Column(db.Enum(Rol), default=Rol.EVALUADOR)
    activo = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relaciones
    evaluaciones = db.relationship('ResultadoEvaluacion', backref='evaluador', lazy=True)
    asociaciones_ronda = db.relationship(
        'ParticipanteRonda',
        back_populates='usuario',
        lazy='dynamic'
    )

    def __repr__(self):
        return f"<Usuario #{self.id}: {self.nombre_usuario}>"

    def guardar(self):
        db.session.add(self)
        db.session.commit()

    def tiene_rol(self, rol: Rol) -> bool:
        return self.rol == rol

    def get_reset_token(self, expires_sec: int = 3600) -> str:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt="password-reset")
        return serializer.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token: str, expires_sec: int = 3600):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt="password-reset")
        try:
            data = serializer.loads(token, max_age=expires_sec)
        except (SignatureExpired, BadData):
            return None
        return Usuario.query.get(data.get('user_id'))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nombre_completo': self.nombre_completo,
            'nombre_usuario': self.nombre_usuario,
            'correo': self.correo,
            'rol': self.rol.value if isinstance(self.rol, Rol) else str(self.rol),
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }
    
    @staticmethod
    def obtener_por_id(usuario_id: int) -> 'Usuario':
        return Usuario.query.get(usuario_id)
    
    @staticmethod
    def obtener_por_nombre_usuario(nombre_usuario: str) -> 'Usuario':
        return Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
    
    @staticmethod
    def obtener_por_correo(correo: str) -> 'Usuario':
        return Usuario.query.filter_by(correo=correo).first()
    
    @staticmethod
    def obtener_todos() -> list:
        return Usuario.query.all()
    
    @staticmethod
    def obtener_activos() -> list:
        return Usuario.query.filter_by(activo=True).all()
    
    @staticmethod
    def obtener_inactivos() -> list:
        return Usuario.query.filter_by(activo=False).all()
    
    @staticmethod
    def obtener_por_rol(rol: Rol) -> list:
        return Usuario.query.filter_by(rol=rol).all()
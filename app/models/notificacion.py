from app.extension import db


# ------------------------
# Modelo Notificacion de evaluacion
# ------------------------
class NotificacionEvaluacion(db.Model):
    __tablename__ = 'notificaciones_evaluacion'

    id = db.Column(db.Integer, primary_key=True)
    usuarios = db.Column(db.String(255), nullable=False)  # Lista de IDs de usuarios separados por comas
    mensaje = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.now())
    leida = db.Column(db.Boolean, default=False)
    id_evaluacion = db.Column(db.Integer, db.ForeignKey('evaluaciones.id'), nullable=True)
    
    evaluacion = db.relationship('Evaluacion', backref='notificaciones', lazy=True)

    def __repr__(self):
        return f"<Notificacion #{self.id} para Usuarios {self.usuarios}>"

    def guardar(self):
        db.session.add(self)
        db.session.commit()
        
    @staticmethod
    def enviar_notificaciones(usuarios: list, mensaje: str, id_evaluacion: int = None) -> 'NotificacionEvaluacion':
        # Ensure usuarios is a list of user IDs, not Usuario objects
        user_ids = [u.id if hasattr(u, 'id') else u for u in usuarios]
        notificacion = NotificacionEvaluacion(
            usuarios=','.join(map(str, user_ids)),
            mensaje=mensaje,
            id_evaluacion=id_evaluacion
        )
        notificacion.guardar()
        return notificacion
        
    
    @staticmethod
    def obtener_todas() -> list:
        return NotificacionEvaluacion.query.all()
    
    @staticmethod
    def obtener_por_id(notificacion_id: int) -> 'NotificacionEvaluacion':
        return NotificacionEvaluacion.query.get(notificacion_id)
    
    @staticmethod
    def eliminar_por_id(notificacion_id: int):
        notificacion = NotificacionEvaluacion.obtener_por_id(notificacion_id)
        if notificacion:
            db.session.delete(notificacion)
            db.session.commit()
            return True
        return False
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'usuarios': self.usuarios.split(',') if self.usuarios else [],
            'mensaje': self.mensaje,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }
    
    @staticmethod
    def obtener_notificaciones_leidas(usuario_id: int) -> list:
        notificaciones = NotificacionEvaluacion.query.filter(
            NotificacionEvaluacion.usuarios.contains(str(usuario_id)),
            NotificacionEvaluacion.leida.is_(True)
        ).all()
        return notificaciones
    
    @staticmethod
    def obtener_mensajes_por_usuario(usuario_id: int) -> list:
        notificaciones = NotificacionEvaluacion.query.filter(NotificacionEvaluacion.usuarios.contains(str(usuario_id))).all()
        return notificaciones

    @staticmethod
    def obtener_aplicaciones_por_usuario(usuario_id: int) -> list:
        notificaciones = NotificacionEvaluacion.query.filter(NotificacionEvaluacion.usuarios.contains(str(usuario_id))).all()
        return [n.id_evaluacion for n in notificaciones]
    
    
# models.py (continuación / actualizaciones)

import datetime
from flask import current_app
from app.extension import db

# ------------------------
# Asociación Usuario ↔ Ronda
# ------------------------
class ParticipanteRonda(db.Model):
    __tablename__ = 'participantes_ronda'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ronda_id = db.Column(db.Integer, db.ForeignKey('rondas_evaluacion.id'), nullable=False)

    invitado_en   = db.Column(db.DateTime, default=datetime.timezone.utc)   # cuándo fue invitado
    ingreso_en    = db.Column(db.DateTime, nullable=True)                   # cuándo empezó la sesión
    ultimo_ping   = db.Column(db.DateTime, nullable=True)                   # última señal de actividad
    salida_en     = db.Column(db.DateTime, nullable=True)                   # cuándo salió / desconectó

    # Relaciones inversas
    usuario = db.relationship('Usuario', back_populates='asociaciones_ronda')
    ronda   = db.relationship('RondaEvaluacion', back_populates='participantes')

    def marcar_ingreso(self):
        """Llamar cuando el usuario se conecta a la ronda."""
        self.ingreso_en = datetime.datetime.utcnow()
        self.ultimo_ping = datetime.datetime.utcnow()
        db.session.commit()

    def ping(self):
        """Actualizar la hora de actividad (heartbeat)."""
        self.ultimo_ping = datetime.datetime.utcnow()
        db.session.commit()

    def marcar_salida(self):
        """Llamar cuando el usuario cierra la sesión o se desconecta."""
        self.salida_en = datetime.datetime.utcnow()
        db.session.commit()

    @property
    def esta_activo(self):
        """
        Determina si el participante está 'conectado':
        - no ha ejecutado marcar_salida()
        - ultimo_ping está dentro del umbral (p. ej. 5 minutos)
        """
        if self.salida_en:
            return False
        if not self.ultimo_ping:
            return False
        delta = datetime.timezone.utc - self.ultimo_ping
        # Umbral configurable en segundos (por defecto 300s = 5min)
        umbral = current_app.config.get('UMBRAL_USUARIO_ACTIVO', 300)
        return delta.total_seconds() <= umbral

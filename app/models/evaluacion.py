from app.extension import db
import datetime

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

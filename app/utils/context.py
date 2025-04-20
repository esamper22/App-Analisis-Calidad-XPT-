# importa modelos todos los modelos obligatoriamente para cargar y crear el conexto
from app.models.aplicacion import  *
from app.models.evaluacion import  *
from app.models.ronda_evaluacion import  *
from app.models.ronda_participantes import  *
from app.models.usuario import  *

def crear_contexto(app):
    
    with app.app_context():
        from ..extension import db
        db.create_all()
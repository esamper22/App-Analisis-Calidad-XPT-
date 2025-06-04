# importa modelos todos los modelos obligatoriamente para cargar y crear el conexto
from app.models.aplicacion import  *
from app.models.evaluacion import  *
from app.models.ronda_evaluacion import  *
from app.models.ronda_participantes import  *
from app.models.usuario import  *

def crear_contexto(app):
    def params_por_defecto():
        '''
        Crea los parametros por defecto para las encuestas de evaluacion de aplicaciones.
        '''
        from app.models.evaluacion import Encuesta
        if not Encuesta.query.filter_by(nombre='Usabilidad').first():
            usabilidad = Encuesta(nombre='Usabilidad', descripcion='Evaluación de la usabilidad de la aplicación')
            usabilidad.guardar()
        if not Encuesta.query.filter_by(nombre='Seguridad').first():
            seguridad = Encuesta(nombre='Seguridad', descripcion='Evaluación de la seguridad de la aplicación')
            seguridad.guardar()
        if not Encuesta.query.filter_by(nombre='Rendimiento').first():
            rendimiento = Encuesta(nombre='Rendimiento', descripcion='Evaluación del rendimiento de la aplicación')
            rendimiento.guardar()
        if not Encuesta.query.filter_by(nombre='Funcionalidad').first():
            funcionalidad = Encuesta(nombre='Funcionalidad', descripcion='Evaluación de la funcionalidad de la aplicación')
            funcionalidad.guardar()
        if not Encuesta.query.filter_by(nombre='Mantenibilidad').first():
            mantenibilidad = Encuesta(nombre='Mantenibilidad', descripcion='Evaluación de la mantenibilidad de la aplicación')
            mantenibilidad.guardar()
        if not Encuesta.query.filter_by(nombre='Portabilidad').first():
            portabilidad = Encuesta(nombre='Portabilidad', descripcion='Evaluación de la portabilidad de la aplicación')
            portabilidad.guardar()
        if not Encuesta.query.filter_by(nombre='Escalabilidad').first():
            escalabilidad = Encuesta(nombre='Escalabilidad', descripcion='Evaluación de la escalabilidad de la aplicación')
            escalabilidad.guardar()
        if not Encuesta.query.filter_by(nombre='Confiabilidad').first():
            confiabilidad = Encuesta(nombre='Confiabilidad', descripcion='Evaluación de la confiabilidad de la aplicación')
            confiabilidad.guardar()
        if not Encuesta.query.filter_by(nombre='Disponibilidad').first():
            disponibilidad = Encuesta(nombre='Disponibilidad', descripcion='Evaluación de la disponibilidad de la aplicación')
            disponibilidad.guardar()
    
    def crear_tipos_applicacion():
        '''
        Crea los tipos de aplicación por defecto.
        '''
        from app.models.aplicacion import TipoAplicacion
        tipos = [
            'Web', 'Móvil', 'Escritorio', 'Híbrida', 'API', 'Microservicio',
            'Servidor', 'Cliente', 'IoT', 'Blockchain', 'Inteligencia Artificial',
            'Realidad Aumentada', 'Realidad Virtual', 'Juego', 'Educativa',
            'Financiera', 'E-commerce', 'Social', 'Salud', 'Productividad',
        ]
        
        for tipo in tipos:
            if not TipoAplicacion.query.filter_by(nombre=tipo).first():
                nuevo_tipo = TipoAplicacion(nombre=tipo, descripcion=f'Tipo de aplicación {tipo}')
                nuevo_tipo.guardar()     
    
    with app.app_context():
        from ..extension import db
        db.create_all()
        
        params_por_defecto()
        crear_tipos_applicacion()
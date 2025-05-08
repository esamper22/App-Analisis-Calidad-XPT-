# config.py

from dotenv import load_dotenv
import os

load_dotenv()

class ConfiguracionBase:
    """Configuración básica para la aplicación."""
    # tu token de acceso, etc.
    TOKEN_ACCESO = os.getenv('TOKEN_ACCESO')
    CLAVE_SECRETA = os.getenv('CLAVE_SECRETA', 'clave-secreta-por-defecto')
    
    # Alias para Email
    MAIL_SERVER   = 'smtp.gmail.com'
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # ¡Alias para Flask!
    SECRET_KEY = CLAVE_SECRETA
    HOST = '0.0.0.0'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ConfiguracionDesarrollo(ConfiguracionBase):
    DEPURACION = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///desarrollo.db'

class ConfiguracionProduccion(ConfiguracionBase):
    DEPURACION = False
    SQLALCHEMY_DATABASE_URI = os.getenv('URI_BASE_DATOS')

configuraciones = {
    'desarrollo': ConfiguracionDesarrollo,
    'produccion': ConfiguracionProduccion,
    'default': ConfiguracionDesarrollo
}

def obtener_configuracion():
    env = os.getenv('FLASK_ENV')
    return configuraciones.get(env, ConfiguracionDesarrollo)

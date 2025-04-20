# config.py

from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# ------------------------
# Configuración de la aplicación Flask
# ------------------------

class ConfiguracionBase:
    """Configuración básica para la aplicación."""
    TOKEN_ACCESO = os.getenv('TOKEN_ACCESO')
    CLAVE_SECRETA = os.getenv('CLAVE_SECRETA', 'clave-secreta-por-defecto')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ConfiguracionDesarrollo(ConfiguracionBase):
    """Configuración para entorno de desarrollo."""
    DEPURACION = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///desarrollo.db'

class ConfiguracionProduccion(ConfiguracionBase):
    """Configuración para entorno de producción/despliegue."""
    DEPURACION = False
    SQLALCHEMY_DATABASE_URI = os.getenv('URI_BASE_DATOS')

# Diccionario para seleccionar la configuración según el entorno
configuraciones = {
    'desarrollo': ConfiguracionDesarrollo,
    'produccion': ConfiguracionProduccion,
    'default': ConfiguracionDesarrollo
}

def obtener_configuracion():
    config = os.getenv('FLASK_ENV')
    return configuraciones.get(config, ConfiguracionDesarrollo)
from flask import Flask
from config import obtener_configuracion

def crear_app():
    app = Flask(__name__)
    app.config.from_object(obtener_configuracion())
    
    from .extension import iniciar_extensiones
    iniciar_extensiones(app)
    
    from .routes import create_routes
    create_routes(app)
    
    from .cli.admin import register_commands
    register_commands(app)
    
    from .utils.context import crear_contexto
    crear_contexto(app)
    
    return app
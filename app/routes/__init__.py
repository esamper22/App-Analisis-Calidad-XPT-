
def create_routes(app):
    # Registrar las rutas de la aplicacion
    
    # Registrar principal
    from app.routes.main import main_bp
    app.register_blueprint(main_bp) # Registrar ruta para usuarios
    
    # Registrar principal
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp) # Registrar ruta para usuarios
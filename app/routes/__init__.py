
def create_routes(app):
    # Registrar las rutas de la aplicacion
    
    # Registrar principal
    from app.routes.main import admin_bp
    app.register_blueprint(admin_bp) # Registrar ruta para usuarios
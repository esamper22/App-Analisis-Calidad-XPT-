
def create_routes(app):
    # Registrar las rutas de la aplicacion
    
    # Registrar principal
    from app.routes.main import main_bp
    app.register_blueprint(main_bp) # Registrar ruta para usuarios
    
    # Registrar principal
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp) # Registrar ruta para usuarios
    
    # Registrar principal
    from app.routes.jefe_dep import jefe_dep_bp
    app.register_blueprint(jefe_dep_bp) # Registrar ruta para jefe departamento
    
    from app.routes.expert import expert_bp
    app.register_blueprint(expert_bp) # Registrar ruta para jefe departamento
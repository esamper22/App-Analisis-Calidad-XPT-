def verificar_admin(app):
    with app.app_context():
        from app.models.usuario import Usuario
        from app.models.rol import Rol
        
        return Usuario.query.filter_by(rol=Rol.ADMIN.value).first()
            
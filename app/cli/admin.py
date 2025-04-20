import click
from werkzeug.security import generate_password_hash

# Mods de Uso:
# flask create-admin
# flask create-admin --username=admin
# flask create-admin --username=admin --password=admin | No recomendado

def register_commands(app):
    @app.cli.command("create-admin")
    @click.option('--username', default='admin', help='Nombre del admin')
    @click.option('--email', prompt=True, required=True, help='Correo electronico')
    @click.option('--password', prompt=True, hide_input=True, 
              confirmation_prompt=True, help='Contraseña del admin')
    
    def crear_admin(username, email, password):
        """Crea un usuario administrador inicial"""
        from app.models.usuario import Usuario
        from app.models.rol import Rol
        from app.extension import db
        
        if Usuario.query.filter_by(nombre_usuario=username).first():
            click.echo(f"⚠️ El usuario '{username}' ya existe.")
            return

        try:
            admin = Usuario(
                nombre_usuario=username,
                correo=email,
                contraseña=generate_password_hash(password),
                rol=Rol.ADMIN.value
            )
            db.session.add(admin)
            db.session.commit()
            click.echo(f"✅ Admin '{username}' creado exitosamente!")
        except Exception as e:
            db.session.rollback()
            click.echo(f"❌ Error: {str(e)}")

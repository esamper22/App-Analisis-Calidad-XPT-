import click
from werkzeug.security import generate_password_hash
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.extension import db

def register_commands(app):
    @app.cli.command("crear-admin")
    @click.option('--username', default='admin', help='Nombre del admin')
    @click.option('--full-name', prompt='Nombre completo', required=True, help='Nombre completo del admin')
    @click.option('--email', prompt=True, required=True, help='Correo electrónico')
    @click.option('--password', prompt=True, hide_input=True, 
                confirmation_prompt=True, help='Contraseña del admin')
    def crear_admin(username, full_name, email, password):
        """Crea un usuario administrador inicial"""
        try:
            if Usuario.query.filter_by(nombre_usuario=username).first():
                click.secho(f"⚠️ El usuario '{username}' ya existe.", fg="yellow")
                return

            admin = Usuario(
                nombre_usuario=username,
                nombre_completo=full_name,
                correo=email,
                contraseña=generate_password_hash(password),
                rol=Rol.ADMIN.value
            )
            
            db.session.add(admin)
            db.session.commit()
            click.secho(f"✅ Admin '{username}' creado exitosamente!", fg="green", bold=True)
            
        except Exception as e:
            db.session.rollback()
            click.secho(f"❌ Error crítico: {str(e)}", fg="red", err=True)
            raise click.Abort()

    @app.cli.command("verificar-admin")
    def verificar_admin():
        """Verifica y obliga a crear admin si no existe"""
        try:
            admin = Usuario.query.filter_by(rol=Rol.ADMIN.value).first()
            
            if admin:
                click.secho(f"✅ Admin existente: {admin.nombre_usuario}", fg="green")
                return
            
            click.secho("🚨 No hay administradores registrados", fg="red")
            click.secho("Ejecuta el siguiente comando para crear uno:", fg="blue")
            click.secho("flask crear-admin --username=<nombre> --full-name=<nombre completo> --email=<correo>", bold=True)
            click.secho("\nO para modo interactivo:", fg="blue")
            click.secho("flask crear-admin", bold=True)
            raise click.Abort()
            
        except Exception as e:
            click.secho(f"🔧 Error de configuración: {str(e)}", fg="red")
            raise click.Abort()

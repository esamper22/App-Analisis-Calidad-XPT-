from functools import wraps
from flask import abort, render_template
from flask_login import current_user
from app.models.usuario import Usuario
from app.models.rol import Rol

def jefe_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica si existe al menos un admin en la base de datos
        jefe_exists = Usuario.query.filter(Usuario.rol == Rol.JEFE_DEPARTAMENTO.value).first() is not None
        if not jefe_exists:
            return render_template('error/no_jefe.html'), 500

        # Verifica si el usuario está autenticado y es admin
        if not current_user.is_authenticated or current_user.rol not in (Rol.JEFE_DEPARTAMENTO):
            abort(403)  # Prohibido

        return f(*args, **kwargs)
    return decorated_function

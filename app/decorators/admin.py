from functools import wraps
from flask import abort, render_template
from flask_login import current_user
from app.models.usuario import User
from app.models.rol import Rol

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica si existe al menos un admin en la base de datos
        admin_exists = User.query.filter(User.role == Rol.SUPERADMIN.value).first() is not None
        if not admin_exists:
            return render_template('error/no_admin.html'), 500

        # Verifica si el usuario está autenticado y es admin
        if not current_user.is_authenticated or current_user.role not in (Rol.SUPERADMIN):
            abort(403)  # Prohibido

        return f(*args, **kwargs)
    return decorated_function

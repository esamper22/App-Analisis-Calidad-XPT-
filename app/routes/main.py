from flask import (
    Blueprint, render_template, request,
    jsonify, redirect, url_for, flash, current_app as app
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash
from app.models.usuario import Usuario
from app.forms.auth.atuenticacion import LoginForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('landing.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    # 1) Si ya está autenticado, lo enviamos al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    # Recoger si es AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # 2) Procesar POST
    if request.method == 'POST':
        # Validar campos CSRF + formatos
        if form.validate_on_submit():
            # Intentar autenticar
            user = Usuario.query.filter_by(
                nombre_usuario=form.usuario.data
            ).first()

            if user and check_password_hash(user.contraseña, form.clave.data):
                login_user(user, remember=form.recordar.data)
                next_url = request.args.get('next') or url_for('admin.dashboard')

                # Respuesta para AJAX
                if is_ajax:
                    return jsonify(success=True, next_url=next_url)

                # Respuesta normal
                return redirect(next_url)

            # Credenciales inválidas
            errors = ['Usuario o contraseña incorrectos.']
        else:
            # Errores de validación WTForms
            errors = [ err for errs in form.errors.values() for err in errs ]

        # Si es AJAX devolvemos JSON con todos los errores
        if is_ajax:
            return jsonify(success=False, errors=errors)

        # Si no es AJAX, caemos al render_template más abajo, con form.errors
        # (puedes mostrar inline con {{ form.usuario.errors }} etc.)

    # 3) GET o POST inválido sin AJAX: renderizamos plantilla
    return render_template(
        'auth/login.html',
        login=form
    )

@main_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    pass

@main_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('main.login_page'))
from flask import (
    Blueprint, render_template, request,
    jsonify, redirect, url_for, flash, current_app as app
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.usuario import Usuario
from app.forms.auth.forgot import ForgotPasswordForm
from app.forms.auth.login import LoginForm
from app.utils.email import send_reset_email
from app.utils.validate_url import is_safe_url
from app.forms.auth.reset import ResetPasswordForm
from app.extension import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('landing.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    enpoint_rol = {'admin': 'admin',
                   'jefe departamento': 'jefe_dep',
                   'evaluador': 'expert'
                   }
    
    # 1) Si ya está autenticado, lo enviamos al dashboard
    if current_user.is_authenticated:
        return redirect(url_for(f'{enpoint_rol[current_user.rol.value]}.dashboard'))

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
                next_url = request.args.get('next') or url_for(f'{enpoint_rol[user.rol.value]}.dashboard')

                # Respuesta para AJAX
                if is_ajax:
                    if next_url and is_safe_url(next_url):
                        return jsonify(success=True, next_url=next_url)
                    return redirect(url_for(f'{enpoint_rol[user.rol.value]}.dashboard'))
                    

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
    form = ForgotPasswordForm()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if form.validate_on_submit():
        user = Usuario.query.filter_by(correo=form.email.data).first()
        if user:
            send_reset_email(user)  
            if is_ajax:
                return jsonify(success=True)
            # en no-AJAX podrías redirigir o mostrar mensaje
        else:
            error = 'No existe un usuario con ese correo.'

            if is_ajax:
                return jsonify(success=False, error=error)

            form.email.errors.append(error)

    if is_ajax and request.method == 'POST':
        # errores de validación WTForms
        first_err = next(iter(form.errors.values()))[0]
        return jsonify(success=False, error=first_err)

    return render_template('auth/forgot_password.html', form=form)

@main_bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    user = Usuario.verify_reset_token(token)
    if not user:
        flash('El enlace de restablecimiento no es válido o ha expirado.', 'warning')
        return redirect(url_for('main.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.contraseña = generate_password_hash(form.clave.data)
        db.session.commit()
        flash('Tu contraseña ha sido actualizada.', 'success')
        return redirect(url_for('main.login_page'))
    return render_template('auth/reset_password.html', form=form)

@main_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('main.login_page'))
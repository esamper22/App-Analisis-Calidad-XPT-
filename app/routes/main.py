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
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = Usuario.query.filter_by(nombre_usuario=form.usuario.data).first()
        if user and check_password_hash(user.contraseña, form.clave.data):
            login_user(user, remember=form.recordar.data)
            next_url = request.args.get('next') or url_for('admin.dashboard')

            # AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(success=True, next_url=next_url)

            flash('Inicio de sesión exitoso.', 'success')
            return redirect(next_url)
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(success=False, error='Credenciales inválidas.')

    elif request.method == 'POST':
        # Mostrar errores del formulario como mensajes flash
        for field_errors in form.errors.values():
            for err in field_errors:
                flash(err, 'danger')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            first_err = next(iter(form.errors.values()))[0]
            return jsonify(success=False, error=first_err)

    return render_template('auth/login.html', login=form)


@main_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    pass

@main_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('main.login_page'))
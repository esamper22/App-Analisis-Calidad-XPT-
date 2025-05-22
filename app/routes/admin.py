from flask import Blueprint, request, jsonify
from flask_wtf.csrf import validate_csrf, CSRFError
from werkzeug.security import generate_password_hash
from app.models.usuario import Usuario
from app.extension import db
from app.models.rol import Rol
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
import re
from flask import current_app
from app.forms.create_user import UsuarioForm, UsuarioEditForm
from app.models.encuesta import Encuesta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def get_users():
    usuarios = Usuario.query.filter(Usuario.id != current_user.id).all()
    return [u.to_json() for u in usuarios]

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    users = Usuario.query.all()
    encuestas = Encuesta.query.all()
    return render_template('dashboard/admin_dashboard.html',
                           users=users,
                           encuestas=encuestas,
                           form_user=UsuarioForm(),
                           )

@admin_bp.route('/listar-usuarios', methods=['GET'])
def listar_usuarios():
    try:
        # Traer todos los usuarios; si quieres excluir al actual, importa current_user y filtra aquí
        usuarios = Usuario.query.all()

        # Serializar cada usuario
        usuarios_data = [u.to_dict() for u in usuarios]
        return jsonify({'usuarios': usuarios_data}), 200

    except Exception:
        db.session.rollback()
        current_app.logger.exception('Error al listar usuarios')
        return jsonify({'error': 'Error interno al obtener usuarios'}), 500

@admin_bp.route('/crear-usuario', methods=['POST'])
def registrar_usuario():
    form = UsuarioForm()

    try:
        # Validar formulario (incluye CSRF)
        if not form.validate_on_submit():
            # Recolectar primer error por campo
            errors = {field: errs[0] for field, errs in form.errors.items()}
            return jsonify({'error': 'Validación', 'fields': errors}), 400

        # Extraer datos limpios
        nombre_completo = form.nombre_completo.data.strip()
        nombre_usuario = form.nombre_usuario.data.strip()
        correo = form.correo.data.strip().lower()
        contraseña = form.contraseña.data
        rol = Rol(form.rol.data)

        # Verificar unicidad (extra, por seguridad)
        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            return jsonify({'error': 'Nombre de usuario ya existe'}), 409
        if Usuario.query.filter_by(correo=correo).first():
            return jsonify({'error': 'Correo ya registrado'}), 409

        # Crear usuario nuevo
        nuevo = Usuario(
            nombre_completo=nombre_completo,
            nombre_usuario=nombre_usuario,
            correo=correo,
            contraseña=generate_password_hash(contraseña),
            rol=rol,
            activo=False
        )
        db.session.add(nuevo)
        db.session.commit()

        # Respuesta exitosa con lista actualizada
        return jsonify({
            'mensaje': 'Usuario creado correctamente',
            'usuarios': get_users()  # Asegúrate que devuelve lista serializable
        }), 201

    except CSRFError:
        return jsonify({'error': 'Token CSRF inválido o expirado'}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Error de integridad en base de datos'}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error al crear usuario: %s', e)
        return jsonify({'error': 'Error interno del servidor'}), 500

@admin_bp.route('/editar-usuario/<int:user_id>', methods=['PUT', 'PATCH'])
def editar_usuario(user_id):
    try:
        if not request.is_json:
            return jsonify({'error': 'Se esperaba JSON'}), 415

        data = request.get_json()

        token = request.headers.get('X-CSRFToken') or request.args.get('csrf_token')
        if token:
            try:
                validate_csrf(token)
            except CSRFError:
                return jsonify({'error': 'Token CSRF inválido o expirado'}), 400

        user = Usuario.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        nombre_usuario = data.get('nombre_usuario', '').strip()
        if not nombre_usuario:
            return jsonify({'error': 'Nombre de usuario es obligatorio'}), 400

        if Usuario.query.filter(Usuario.nombre_usuario == nombre_usuario, Usuario.id != user_id).first():
            return jsonify({'error': 'Nombre de usuario en uso'}), 409

        form_data = {k: v for k, v in data.items() if k != 'nombre_usuario'}
        form = UsuarioEditForm(data=form_data, meta={'csrf': False})

        if not form.validate():
            errors = {field: errs[0] for field, errs in form.errors.items()}
            return jsonify({'error': 'Validación', 'fields': errors}), 400

        user.nombre_completo = form.nombre_completo.data.strip()
        user.nombre_usuario = nombre_usuario
        user.correo = form.correo.data.strip().lower()

        try:
            user.rol = Rol(form.rol.data.strip().lower())
        except ValueError:
            return jsonify({'error': 'Rol inválido'}), 400

        if 'contraseña' in data:
            pwd = data['contraseña']
            if not isinstance(pwd, str) or len(pwd) < 6:
                return jsonify({'error': 'Contraseña inválida (mínimo 6 caracteres)'}), 400
            user.contraseña = generate_password_hash(pwd)

        if 'activo' in data:
            act = data['activo']
            if not isinstance(act, bool):
                return jsonify({'error': 'Campo activo debe ser booleano'}), 400
            user.activo = act

        db.session.commit()

        return jsonify({
            'mensaje': 'Usuario actualizado correctamente',
            'usuarios': get_users()
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Conflicto al actualizar, datos duplicados'}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error al editar usuario: %s', e)
        return jsonify({'error': 'Error interno del servidor'}), 500

@admin_bp.route('/eliminar-usuario/<int:user_id>', methods=['DELETE'])
def eliminar_usuario(user_id):
    try:
        user = Usuario.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({'mensaje': 'Usuario eliminado correctamente', 
                        'usuarios': get_users()}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error al eliminar usuario')
        return jsonify({'error': 'Error interno del servidor'}), 500

@admin_bp.route('/obtener-usuario/<int:user_id>', methods=['GET'])
def obtener_usuario(user_id):
    try:
        user = Usuario.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Serializar usuario
        usuario_data = {
            'id': user.id,
            'nombre_completo': user.nombre_completo,
            'nombre_usuario': user.nombre_usuario,
            'correo': user.correo,
            'rol': user.rol.value if hasattr(user.rol, 'value') else str(user.rol),
            'activo': user.activo
        }
        return jsonify({'usuario': usuario_data})

    except Exception as e:
        current_app.logger.exception('Error al obtener usuario')
        return jsonify({'error': 'Error interno del servidor'}), 500

    user = Usuario.query.get(id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Devolver datos relevantes en JSON
    return jsonify(user.to_json()), 200
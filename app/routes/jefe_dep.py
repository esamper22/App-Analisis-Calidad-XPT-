from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.models.encuesta import Encuesta
from flask_login import login_required
from app.extension import db
from app.models.usuario import Usuario
from app.forms.create_user import UsuarioForm
from app.decorators.jefe_dep import jefe_required

jefe_dep_bp = Blueprint('jefe_dep', __name__, url_prefix='/jefe_dep')


def validar_pregunta(texto):
    if not texto or not texto.strip():
        return 'La pregunta es requerida.'
    if len(texto.strip()) > 500:
        return 'La pregunta no puede exceder 500 caracteres.'
    return None

def get_all_encuestas():
    encuestas = Encuesta.query.all()
    return [encuesta.to_dict() for encuesta in encuestas]


@jefe_dep_bp.route('/encuestas', methods=['POST'])
@login_required
@jefe_required
def crear_encuesta():
    """
    Crea una nueva encuesta con la pregunta proporcionada.
    """
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'JSON inválido o Content-Type incorrecto.'}), 400

    error = validar_pregunta(data.get('pregunta', ''))
    if error:
        return jsonify({'error': error}), 400

    try:
        nueva = Encuesta(pregunta=data['pregunta'].strip())
        db.session.add(nueva)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Error al guardar en la base de datos.'}), 500

    return jsonify({
        'message': 'Encuesta creada',
        'encuestas': get_all_encuestas()
    }), 201

@jefe_dep_bp.route('/dashboard')
@login_required
@jefe_required
def dashboard():
    users = Usuario.query.all()
    encuestas = Encuesta.query.all()
    return render_template('dashboard/admin_dashboard.html',
                           users=users,
                           encuestas=encuestas,
                           form_user=UsuarioForm(),
                           )

@jefe_dep_bp.route('/encuestas/<int:id>', methods=['PUT'])
@login_required
@jefe_required
def editar_encuesta(id):
    """
    Actualiza la pregunta de una encuesta existente.
    """
    encuesta = Encuesta.query.get_or_404(id)

    data = request.get_json()
    if data is None:
        return jsonify({'error': 'JSON inválido o Content-Type incorrecto.'}), 400

    error = validar_pregunta(data.get('pregunta', ''))
    if error:
        return jsonify({'error': error}), 400

    try:
        encuesta.pregunta = data['pregunta'].strip()
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar en la base de datos.'}), 500

    return jsonify({
        'message': 'Encuesta actualizada',
        'encuestas': get_all_encuestas()
    })

@jefe_dep_bp.route('/encuestas/<int:id>', methods=['DELETE'])
@login_required
@jefe_required
def eliminar_encuesta(id):
    """
    Elimina una encuesta por ID.
    """
    encuesta = Encuesta.query.get_or_404(id)
    try:
        db.session.delete(encuesta)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar de la base de datos.'}), 500

    return jsonify({
        'message': 'Encuesta eliminada',
        'encuestas': get_all_encuestas()
    })

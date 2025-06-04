import datetime
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.models.evaluacion import Encuesta, EvaluacionParametro, EvaluacionUsuario, Evaluacion
from flask_login import login_required

from app.extension import db
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.forms.create_user import UsuarioForm
from app.decorators.jefe_dep import jefe_required
from app.models.aplicacion import Aplicacion, TipoAplicacion
from app.utils.iconos import obtener_iconos_bootstrap
from app.models.evaluacion import Encuesta, Evaluacion

jefe_dep_bp = Blueprint('jefe_dep', __name__, url_prefix='/jefe_dep')



# ---------------------------------------------------------------------
#                       Validaciones y Serialización                  #
# ---------------------------------------------------------------------

def validar_pregunta(texto):
    if not texto or not texto.strip():
        return 'La pregunta es requerida.'
    if len(texto.strip()) > 500:
        return 'La pregunta no puede exceder 500 caracteres.'
    return None

def serializar(data=None):
    return [d.to_dict() for d in data]



# -----------------------------------------------------------------
#                       PANEL JEFE DEPARTAMENTO                   #
# -----------------------------------------------------------------

@jefe_dep_bp.route('/dashboard')
@login_required
@jefe_required
def dashboard():
    users = Usuario.query.all()
    evaluadores = Usuario.obtener_por_rol(rol=Rol.EVALUADOR)
    # encuestas = Encuesta.query.all()
    
    return render_template('dashboard/jefe_departamento.html',
                           users=users,
                        #    encuestas=encuestas,
                           form_user=UsuarioForm(),
                           tipos_aplicacion = serializar(TipoAplicacion.obtener_todos()),
                           apps=serializar(Aplicacion.obtener_todas()),
                           evaluadores=serializar(evaluadores),
                           iconos_bootstrap=obtener_iconos_bootstrap(),
                           parametros=serializar(Encuesta.obtener_todos()),
                           )



# -----------------------------------------------------------------
#                            Encuestas                            #
# -----------------------------------------------------------------

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
        'encuestas': serializar(Encuesta.obtener_todas())
    }), 201

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
        'encuestas': serializar(Encuesta.obtener_todas())
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
        encuesta.eliminar()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar de la base de datos.'}), 500

    return jsonify({
        'message': 'Encuesta eliminada',
        'encuestas': serializar(Encuesta.obtener_todas())
    })


# -----------------------------------------------------------------
#                       APLICACIONES                              #
# -----------------------------------------------------------------

@jefe_dep_bp.route('/aplicacion', methods=['POST'])
@login_required
@jefe_required
def crear_aplicacion():
    """
    Crea una nueva aplicación de encuesta vía JSON (AJAX).
    """
    
    data = request.get_json()
    
     # Leer los datos desde request.form en lugar de get_json()
    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()
    tipo_id = data.get('tipo_aplicacion_id', '').strip()
    version = data.get('version', '').strip()
    icono = data.get('icono', '').strip()
    
    # Validar campos requeridos
    required_fields = ['nombre', 'descripcion', 'tipo_aplicacion_id', 'icono']
    missing = [field for field in required_fields if not data.get(field, '').strip()]
    print(missing)
    if missing:
        return jsonify({'error': f'Faltan campos requeridos: {", ".join(missing)}'}), 400

    # Validar tipo de aplicación
    tipo_aplicacion = TipoAplicacion.obtener_por_id(tipo_id)
    if not tipo_aplicacion:
        return jsonify({'error': 'Tipo de aplicación no encontrado.'}), 404

    try:
        nueva_app = Aplicacion(
            nombre=nombre,
            descripcion=descripcion,
            tipo_aplicacion_id=tipo_aplicacion.id,
            version=version or '1.0',
            icono=icono,
        )
        db.session.add(nueva_app)
        db.session.commit()
        return jsonify({'message': 'Aplicación creada exitosamente.', 'apps': serializar(Aplicacion.obtener_todas()) }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear la aplicación: {e}")
        return jsonify({'error': 'Error al crear la aplicación', 'details': str(e)}), 500

@jefe_dep_bp.route('/aplicacion/<int:app_id>', methods=['PUT'])
@login_required
@jefe_required
def editar_aplicacion(app_id):
    """
    Edita una aplicación existente vía JSON (AJAX).
    """
    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()
    tipo_id = data.get('tipo_aplicacion_id', '').strip()
    version = data.get('version', '').strip()
    icono = data.get('icono', '').strip()

    # Validar campos requeridos
    required_fields = ['nombre', 'descripcion', 'tipo_aplicacion_id', 'icono']
    missing = [field for field in required_fields if not data.get(field, '').strip()]
    if missing:
        return jsonify({'error': f'Faltan campos requeridos: {", ".join(missing)}'}), 400

    # Buscar la aplicación
    aplicacion = Aplicacion.query.get(app_id)
    if not aplicacion:
        return jsonify({'error': 'Aplicación no encontrada.'}), 404

    # Validar tipo de aplicación
    tipo_aplicacion = TipoAplicacion.obtener_por_id(tipo_id)
    if not tipo_aplicacion:
        return jsonify({'error': 'Tipo de aplicación no encontrado.'}), 404

    try:
        aplicacion.nombre = nombre
        aplicacion.descripcion = descripcion
        aplicacion.tipo_aplicacion_id = tipo_aplicacion.id
        aplicacion.version = version or aplicacion.version
        aplicacion.icono = icono
        db.session.commit()
        return jsonify({
            'message': 'Aplicación actualizada exitosamente.',
            'apps': serializar(Aplicacion.obtener_todas())
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar la aplicación', 'details': str(e)}), 500

@jefe_dep_bp.route('/aplicacion', methods=['GET'])
@login_required
@jefe_required
def obtener_aplicaciones():
    """
    Devuelve todas las aplicaciones en formato JSON.
    """
    try:
        aplicaciones = Aplicacion.obtener_todas()
        return jsonify({
            'apps': serializar(aplicaciones)
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener las aplicaciones', 'details': str(e)}), 500

@jefe_dep_bp.route('/aplicacion', methods=['GET'])
@login_required
@jefe_required
def buscar_aplicaciones():
    """
    Busca aplicaciones por nombre o descripción.
    """
    q = request.args.get('search', '').strip()
    
    if not q:
        return jsonify({'error': 'Parámetro de búsqueda vacío.'}), 400

    try:
        aplicaciones = Aplicacion.buscar_por_cualquier_parametro(q)
        return jsonify({
            'apps': serializar(aplicaciones)
        }), 200
    except Exception as e:
        return jsonify({'error': 'Error al buscar aplicaciones', 'details': str(e)}), 500

@jefe_dep_bp.route('/aplicacion/<int:app_id>', methods=['DELETE'])
@login_required
@jefe_required
def eliminar_aplicacion(app_id):
    """
    Elimina una aplicación existente vía AJAX.
    """
    aplicacion = Aplicacion.query.get(app_id)
    if not aplicacion:
        return jsonify({'error': 'Aplicación no encontrada.'}), 404

    try:
        db.session.delete(aplicacion)
        db.session.commit()
        return jsonify({
            'message': 'Aplicación eliminada exitosamente.',
            'apps': serializar(Aplicacion.obtener_todas())
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar la aplicación', 'details': str(e)}), 500


# -----------------------------------------------------------------
#                       TIPOS DE APLICACION                       #
# -----------------------------------------------------------------
@jefe_dep_bp.route('/tipo_aplicacion', methods=['POST'])
@login_required
@jefe_required
def crear_tipo_aplicacion():
    """
    Crea un nuevo TipoAplicacion a partir de JSON enviado por AJAX.
    Espera { 'nombre': ..., 'descripcion': ... } en request.get_json().
    Retorna JSON { success: True, tipos: [...] } o { success: False, message: ... }.
    """
    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()

    if not nombre:
        return jsonify(success=False, message='El nombre es obligatorio.'), 400

    existente = TipoAplicacion.buscar_por_nombre(nombre)
    if existente:
        return jsonify(success=False, message='Ya existe un tipo con ese nombre.'), 409

    try:
        nuevo_tipo = TipoAplicacion(nombre=nombre, descripcion=descripcion or None)
        db.session.add(nuevo_tipo)
        db.session.commit()
        # Devolver la lista completa de tipos para refrescar el front-end
        tipos = [t.to_dict() for t in TipoAplicacion.obtener_todos()]
        return jsonify(success=True, message='Tipo creado exitosamente.', tipos=tipos), 201
    except Exception:
        db.session.rollback()
        return jsonify(success=False, message='Error al guardar el nuevo tipo.'), 500


@jefe_dep_bp.route('/tipo_aplicacion', methods=['GET'])
@login_required
@jefe_required
def obtener_tipos_aplicacion():
    """
    Devuelve todos los tipos de aplicación en formato JSON.
    Retorna JSON { success: True, tipos: [...] } o { success: False, message: ... }.
    """
    try:
        return jsonify(success=True, tipos=serializar(TipoAplicacion.obtener_todos())), 200
    except Exception as e:
        return jsonify(success=False, message='Error al obtener los tipos de aplicación.'), 500

@jefe_dep_bp.route('/tipo_aplicacion/<int:tipo_id>', methods=['PUT'])
@login_required
@jefe_required
def editar_tipo_aplicacion(tipo_id):
    """
    Edita un TipoAplicacion existente vía AJAX JSON.
    Espera { 'nombre': ..., 'descripcion': ... } en request.get_json().
    Retorna JSON { success: True, tipos: [...] } o { success: False, message: ... }.
    """
    tipo = TipoAplicacion.obtener_por_id(tipo_id)
    if not tipo:
        return jsonify(success=False, message='Tipo no encontrado.'), 404

    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()

    if not nombre:
        return jsonify(success=False, message='El nombre es obligatorio.'), 400

    # Verificar si existe otro tipo con el mismo nombre
    otro = TipoAplicacion.query.filter(
        TipoAplicacion.nombre == nombre,
        TipoAplicacion.id != tipo_id
    ).first()
    if otro:
        return jsonify(success=False, message='Ya existe otro tipo con ese nombre.'), 409

    try:
        tipo.nombre = nombre
        tipo.descripcion = descripcion or None
        db.session.commit()
        tipos = [t.to_dict() for t in TipoAplicacion.obtener_todos()]
        return jsonify(success=True, message='Tipo actualizado exitosamente.', tipos=tipos), 200
    except Exception:
        db.session.rollback()
        return jsonify(success=False, message='Error al actualizar el tipo.'), 500


@jefe_dep_bp.route('/tipo_aplicacion/<int:tipo_id>', methods=['DELETE'])
@login_required
@jefe_required
def eliminar_tipo_aplicacion(tipo_id):
    """
    Elimina un TipoAplicacion existente vía AJAX.
    Retorna JSON { success: True, tipos: [...] } o { success: False, message: ... }.
    """
    tipo = TipoAplicacion.obtener_por_id(tipo_id)
    if not tipo:
        return jsonify(success=False, message='Tipo no encontrado.'), 404

    try:
        db.session.delete(tipo)
        db.session.commit()
        tipos = [t.to_dict() for t in TipoAplicacion.obtener_todos()]
        return jsonify(success=True, message='Tipo eliminado exitosamente.', tipos=tipos), 200
    except Exception:
        db.session.rollback()
        return jsonify(success=False, message='Error al eliminar el tipo.'), 500



# -----------------------------------------------------------------
#                       PARAMETROS EVALUACION                     #
# -----------------------------------------------------------------
@jefe_dep_bp.route('/parametro_evaluacion', methods=['GET'])
@login_required
@jefe_required
def obtener_parametros_evaluacion():
    """
    Devuelve todos los parámetros de evaluación en formato JSON.
    Retorna JSON { success: True, parametros: [...] } o { success: False, message: ... }.
    """
    try:
        parametros = Encuesta.obtener_todos()
        return jsonify(success=True, parametros=serializar(parametros)), 200
    except Exception as e:
        return jsonify(success=False, message='Error al obtener los parámetros de evaluación.'), 500

@jefe_dep_bp.route('/parametro_evaluacion', methods=['POST'])
@login_required
@jefe_required
def crear_parametro_evaluacion():
    """
    Crea un nuevo parámetro de evaluación.
    Espera un JSON con 'nombre', 'descripcion', 'tipo', 'peso', 'peso_minimo', 'peso_maximo' y opcionalmente 'estados'.
    Retorna un JSON con el parámetro creado o un error.
    """
    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()
    # tipo = data.get('tipo', '').strip()  # 'numerico', 'texto', 'booleano'
    pesos = data.get('pesos', '2.0,3.0,4.0,5.0')
    estados = data.get('estados', 'mal,regular,bien,excelente')

    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio.'}), 400

    # tipos_validos = ['numerico', 'texto', 'booleano']
    # if tipo not in tipos_validos:
    #     return jsonify({'error': f'Tipo inválido. Debe ser uno de: {", ".join(tipos_validos)}.'}), 400

    # Validar pesos
    try:
        pesos_lista = [float(p) for p in pesos]
        if len(pesos_lista) < 2:
            return jsonify({'error': 'Debe proporcionar al menos dos pesos.'}), 400
        if any(p <= 0 for p in pesos_lista):
            return jsonify({'error': 'Todos los pesos deben ser números positivos.'}), 400
    except ValueError:
        return jsonify({'error': 'Los pesos deben ser números válidos separados por comas.'}), 400
    
    
    # Validar pesos y estados tengan la misma cantidad
    if estados:
        if len(estados) != len(pesos_lista):
            return jsonify({'error': 'La cantidad de estados debe coincidir con la cantidad de pesos.'}), 400
        

    existente = Encuesta.query.filter_by(nombre=nombre).first()
    if existente:
        return jsonify({'error': 'Ya existe un parámetro con ese nombre.'}), 409

    try:
        nuevo_parametro = Encuesta(
            nombre=nombre,
            descripcion=descripcion,
            # tipo=tipo,
            pesos= ",".join([str(peso) for peso in pesos]),
            estados=",".join([estado for estado in estados])
        )
        db.session.add(nuevo_parametro)
        db.session.commit()
        return jsonify({
            'message': 'Parámetro creado exitosamente.',
            'parametros': serializar(Encuesta.obtener_todos())
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@jefe_dep_bp.route('/parametro_evaluacion/<int:parametro_id>', methods=['PUT'])
@login_required
@jefe_required
def editar_parametro_evaluacion(parametro_id):
    """
    Edita un parámetro de evaluación existente.
    Espera un JSON con 'nombre', 'descripcion', 'tipo', 'peso', 'peso_minimo', 'peso_maximo' y opcionalmente 'estados'.
    Retorna un JSON con el parámetro actualizado o un error.
    """
    parametro = Encuesta.obtener_por_id(parametro_id)
    if not parametro:
        return jsonify({'error': 'Parámetro no encontrado.'}), 404

    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()
    # tipo = data.get('tipo', '').strip()
    pesos = data.get('pesos', '2.0,3.0,4.0,5.0')
    estados = data.get('estados', parametro.estados)

    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio.'}), 400

    # tipos_validos = ['numerico', 'texto', 'booleano']
    # if tipo and tipo not in tipos_validos:
    #     return jsonify({'error': f'Tipo inválido. Debe ser uno de: {", ".join(tipos_validos)}.'}), 400

    # Validar pesos
    try:
        pesos_lista = [float(p) for p in pesos]
        if len(pesos_lista) < 2:
            return jsonify({'error': 'Debe proporcionar al menos dos pesos.'}), 400
        if any(p <= 0 for p in pesos_lista):
            return jsonify({'error': 'Todos los pesos deben ser números positivos.'}), 400
    except ValueError:
        return jsonify({'error': 'Los pesos deben ser números válidos separados por comas.'}), 400
    
    # Validar pesos y estados tengan la misma cantidad
    if estados:
        if len(estados) != len(pesos_lista):
            return jsonify({'error': 'La cantidad de estados debe coincidir con la cantidad de pesos.'}), 400
    
    otro = Encuesta.query.filter(
        Encuesta.nombre == nombre,
        Encuesta.id != parametro_id
    ).first()
    if otro:
        return jsonify({'error': 'Ya existe otro parámetro con ese nombre.'}), 409

    try:
        parametro.nombre = nombre
        parametro.descripcion = descripcion
        # if tipo:
        #     parametro.tipo = tipo
        parametro.peso = ",".join([str(peso) for peso in pesos])
        parametro.estados = ",".join([estado for estado in estados])
        db.session.commit()
        return jsonify({
            'message': 'Parámetro actualizado exitosamente.',
            'parametros': serializar(Encuesta.obtener_todos())
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@jefe_dep_bp.route('/parametro_evaluacion/<int:parametro_id>', methods=['DELETE'])
@login_required
@jefe_required
def eliminar_parametro_evaluacion(parametro_id):
    """
    Elimina un parámetro de evaluación existente.
    Retorna un JSON con el mensaje de éxito o un error.
    """
    parametro = Encuesta.obtener_por_id(parametro_id)
    if not parametro:
        return jsonify({'error': 'Parámetro no encontrado.'}), 404

    try:
        db.session.delete(parametro)
        db.session.commit()
        return jsonify({
            'message': 'Parámetro eliminado exitosamente.',
            'parametros': serializar(Encuesta.obtener_todos())
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# -----------------------------------------------------------------
#                           EVALUACION                            #
# -----------------------------------------------------------------
@jefe_dep_bp.route('/evaluacion', methods=['GET'])
@login_required
@jefe_required
def obtener_evaluaciones():
    """
    Devuelve todas las evaluaciones en formato JSON.
    Retorna JSON { success: True, evaluaciones: [...] } o { success: False, message: ... }.
    """
    try:
        evaluaciones = Evaluacion.obtener_todos()
        return jsonify(success=True, evaluaciones=serializar(evaluaciones)), 200
    except Exception as e:
        print(f"Error al obtener evaluaciones: {e}")
        return jsonify(success=False, message='Error al obtener las evaluaciones.'), 500


@jefe_dep_bp.route('/evaluacion', methods=['POST'])
@login_required
@jefe_required
def crear_evaluacion():
    """
    Crea una nueva evaluación.
    Espera un JSON con:
      - app_id: int
      - parametros: [int, int, ...]     (lista de IDs de Encuesta)
      - usuarios: [int, int, ...]    (lista de IDs de Usuario)
      - fecha_inicio: "YYYY-MM-DD"
      - fecha_fin:    "YYYY-MM-DD"
      - rondas: int (opcional, por defecto 1)
      - comentarios: string (opcional)
    Retorna JSON con mensaje y la lista completa de evaluaciones.
    """
    data = request.get_json() or {}

    app_id = data.get('aplicacion_id')
    lista_parametros = data.get('parametros', [])
    lista_evaluadores = data.get('usuarios', [])
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    rondas = data.get('rondas', 1)
    comentarios = data.get('comentarios', '')
    
    # Depuracion
    print("Insertando Evaluacion")
    print(f"app_id: {app_id}, lista_parametros: {lista_parametros}, lista_evaluadores: {lista_evaluadores}, fecha_inicio: {fecha_inicio}, fecha_fin: {fecha_fin}, rondas: {rondas}, comentarios: {comentarios}")
    
    # Validaciones básicas
    if not app_id or not lista_parametros or not lista_evaluadores or not fecha_inicio or not fecha_fin:
        return jsonify(error='Faltan campos obligatorios.'), 400

    # Verificar aplicación
    app_obj = Aplicacion.obtener_por_id(app_id)
    if not app_obj:
        return jsonify(error='Aplicación no encontrada.'), 404

    # Verificar que todos los parámetros existan
    encuestas_objs = Encuesta.query.filter(Encuesta.id.in_(lista_parametros)).all()
    if len(encuestas_objs) != len(lista_parametros):
        return jsonify(error='Algún parámetro de evaluación no existe.'), 404

    # Verificar que todos los usuarios existan
    usuarios_objs = Usuario.query.filter(Usuario.id.in_(lista_evaluadores)).all()
    if len(usuarios_objs) != len(lista_evaluadores):
        return jsonify(error='Algún evaluador no existe.'), 404
    
    # Parsear fechas
    try:
        fi = datetime.datetime.fromisoformat(fecha_inicio)
        ff = datetime.datetime.fromisoformat(fecha_fin)
    except Exception:
        return jsonify(error='Formato de fecha inválido. Use YYYY-MM-DD.'), 400

    if ff < fi:
        return jsonify(error='La fecha de fin no puede ser anterior a la fecha de inicio.'), 400

    try:
        # Crear Evaluacion
        nueva_eval = Evaluacion(
            aplicacion_id=app_id,
            fecha_inicio=fi,
            fecha_fin=ff,
            rondas=rondas,
            comentarios=comentarios
        )
        db.session.add(nueva_eval)
        db.session.flush()  # Para obtener nueva_eval.id

        # Asociar parámetros (muchos-a-muchos)
        for encuesta_obj in encuestas_objs:
            nueva_eval.parametros.append(encuesta_obj)

        # Asociar evaluadores (muchos-a-muchos)
        for usuario_obj in usuarios_objs:
            nueva_eval.usuarios.append(usuario_obj)

        db.session.commit()

        todas = Evaluacion.obtener_todos()
        return jsonify(
            message='Evaluación creada exitosamente.',
            evaluaciones=[e.to_dict() for e in todas]
        ), 201

    except Exception as ex:
        db.session.rollback()
        return jsonify(error='Error al crear la evaluación.', details=str(ex)), 500


@jefe_dep_bp.route('/evaluacion/<int:eval_id>', methods=['PUT'])
@login_required
@jefe_required
def editar_evaluacion(eval_id):
    """
    Edita una evaluación existente.
    Espera un JSON con el mismo esquema que en POST:
      - app_id: int
      - parametros: [int, int, ...]
      - evaluadores: [int, int, ...]
      - fecha_inicio: YYYY-MM-DD
      - fecha_fin:    YYYY-MM-DD
      - rondas: int
      - comentarios: str
    Retorna JSON con mensaje y lista completa de evaluaciones.
    """
    eval_obj = Evaluacion.obtener_por_id(eval_id)
    if not eval_obj:
        return jsonify(error='Evaluación no encontrada.'), 404

    data = request.get_json() or {}
    app_id = data.get('aplicacion_id')
    lista_parametros = data.get('parametros', [])
    lista_evaluadores = data.get('usuarios', [])
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    rondas = data.get('rondas', eval_obj.rondas)
    comentarios = data.get('comentarios', eval_obj.comentarios)

    if not app_id or not lista_parametros or not lista_evaluadores or not fecha_inicio or not fecha_fin:
        return jsonify(error='Faltan campos obligatorios.'), 400

    # Verificar aplicación
    app_obj = Aplicacion.obtener_por_id(app_id)
    if not app_obj:
        return jsonify(error='Aplicación no encontrada.'), 404

    # Verificar parámetros
    encuestas_objs = Encuesta.query.filter(Encuesta.id.in_(lista_parametros)).all()
    if len(encuestas_objs) != len(lista_parametros):
        return jsonify(error='Algún parámetro de evaluación no existe.'), 404

    # Verificar usuarios
    usuarios_objs = Usuario.query.filter(Usuario.id.in_(lista_evaluadores)).all()
    if len(usuarios_objs) != len(lista_evaluadores):
        return jsonify(error='Algún evaluador no existe.'), 404

    # Parsear fechas
    try:
        fi = datetime.datetime.fromisoformat(fecha_inicio)
        ff = datetime.datetime.fromisoformat(fecha_fin)
    except Exception:
        return jsonify(error='Formato de fecha inválido. Use YYYY-MM-DD.'), 400

    if ff < fi:
        return jsonify(error='La fecha de fin no puede ser anterior a la fecha de inicio.'), 400

    try:
        # 1) Actualizar campos básicos
        eval_obj.aplicacion_id = app_id
        eval_obj.fecha_inicio = fi
        eval_obj.fecha_fin = ff
        eval_obj.rondas = rondas
        eval_obj.comentarios = comentarios

        # 2) Limpiar asociaciones parámetros y volver a agregar
        eval_obj.parametros.clear()
        for encuesta_obj in encuestas_objs:
            eval_obj.parametros.append(encuesta_obj)

        # 3) Limpiar asociaciones usuarios y volver a agregar
        eval_obj.usuarios.clear()
        for usuario_obj in usuarios_objs:
            eval_obj.usuarios.append(usuario_obj)

        db.session.commit()

        todas = Evaluacion.obtener_todos()
        return jsonify(
            message='Evaluación actualizada exitosamente.',
            evaluaciones=[e.to_dict() for e in todas]
        ), 200

    except Exception as ex:
        db.session.rollback()
        return jsonify(error='Error al actualizar la evaluación.', details=str(ex)), 500

    

@jefe_dep_bp.route('/evaluacion/<int:eval_id>', methods=['DELETE'])
@login_required
@jefe_required
def eliminar_evaluacion(eval_id):
    """
    Elimina una evaluación y sus asociaciones intermedias.
    """
    eval_obj = Evaluacion.obtener_por_id(eval_id)
    if not eval_obj:
        return jsonify(error='Evaluación no encontrada.'), 404

    try:
        # Las relaciones muchos-a-muchos se manejan automáticamente porque
        # en el modelo se definieron como `secondary` sin `cascade="all, delete"`.
        # Así que basta eliminar el registro padre:
        db.session.delete(eval_obj)
        db.session.commit()

        todas = Evaluacion.obtener_todos()
        return jsonify(
            message='Evaluación eliminada exitosamente.',
            evaluaciones=[e.to_dict() for e in todas]
        ), 200

    except Exception as ex:
        db.session.rollback()
        return jsonify(error='Error al eliminar la evaluación.', details=str(ex)), 500


@jefe_dep_bp.route('/evaluacion/<int:evaluacion_id>/enviar', methods=['POST'])
@login_required
@jefe_required
def enviar_evaluacion(evaluacion_id):
    """
    Marca la evaluación como 'enviado' y notifica a todos los evaluadores relacionados.
    Devuelve JSON con el estado actualizado y la lista de evaluaciones.
    """
    evaluacion = Evaluacion.obtener_por_id(evaluacion_id)
    if not evaluacion:
        return jsonify({'error': 'Evaluación no encontrada.'}), 404

    try:
        # Cambiar estado de la evaluación a "enviado"
        evaluacion.estado = 'enviado'
        db.session.commit()

        # (Opcional) Aquí podrías iterar sobre evaluacion.usuarios para enviar notificaciones.
        # for usuario in evaluacion.usuarios:
        #     enviar_notificacion(usuario.email, evaluacion)

        # Devolver lista actualizada de evaluaciones
        todas = [e.to_dict() for e in Evaluacion.obtener_todos()]
        return jsonify({
            'message': 'Evaluación enviada a todos los evaluadores.',
            'evaluaciones': todas
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'No se pudo enviar la evaluación: {str(e)}'}), 500




# -----------------------------------------------------------------
#                       ACTUALIZAR TODO                           #
# -----------------------------------------------------------------
@jefe_dep_bp.route('/actualizar_todo', methods=['GET'])
@login_required
@jefe_required
def actualizar_todo():
    """
    Actualiza todos los datos necesarios en el dashboard del jefe de departamento.
    Retorna un JSON con los datos actualizados.
    """
    try:
        users = Usuario.query.all()
        # encuestas = Encuesta.query.all()
        aplicaciones = Aplicacion.obtener_todas()
        tipos_aplicacion = TipoAplicacion.obtener_todos()

        return jsonify({
            'users': serializar(users),
            'aplicaciones': serializar(aplicaciones),
            'tipos_aplicacion': serializar(tipos_aplicacion),
            # 'encuestas': serializar(encuestas),
            'parametros': serializar(Encuesta.obtener_todos()),
            'iconos_bootstrap': obtener_iconos_bootstrap(),
            'evaluacion': serializar(Evaluacion.obtener_todos())
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
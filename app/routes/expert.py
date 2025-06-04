# app/routes/expert.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from itsdangerous import URLSafeTimedSerializer, BadData, SignatureExpired
from datetime import datetime, date, timedelta

from app.extension import db
from app.models.aplicacion import Aplicacion, TipoAplicacion
from app.models.evaluacion import Evaluacion, EvaluacionUsuario, EvaluacionParametro
from app.models.encuesta import Encuesta
from app.models.usuario import Usuario
from app.models.notificacion import NotificacionEvaluacion
from app.models.resultado import ResultadoEvaluacion
from app.models.rol import Rol
from app.decorators.expert import expert_required
from app.forms.update_account import UpdateAccountForm

expert_bp = Blueprint('expert', __name__, url_prefix='/expert')


# ---------------------------------------------
# 1) Dashboard y páginas principales
# ---------------------------------------------
@expert_bp.route('/dashboard')
@login_required
@expert_required
def dashboard():
    # 1. Último login (simulado si no existiera campo real)
    last_login = getattr(current_user, 'last_login', datetime.now())

    # 2. Notificaciones del evaluador (dropdown superior)
    notifications = NotificacionEvaluacion.obtener_notificaciones_leidas(current_user.id)

    # 3. Evaluaciones en las que el usuario ha sido notificado y están pendientes
    evs_notificados = Evaluacion.obtener_evaluaciones_notificados(current_user.id)
    # Agrupar esas evaluaciones por aplicación
    apps_dict = {}
    for ev in evs_notificados:
        app_obj = ev.aplicacion
        if not app_obj:
            continue
        if app_obj.id not in apps_dict:
            apps_dict[app_obj.id] = {
                'aplicacion_obj': app_obj,
                'evaluaciones': []
            }
        # Calcular propiedades para el template:
        #  - parametro_nombre: nombre del primer parámetro asociado (si existe)
        parametro_nombre = ev.parametros[0].nombre if ev.parametros else '–'
        #  - estado_badge: mapeo a clase Bootstrap
        badge_map = {
            'pendiente': 'warning',
            'en progreso': 'info',
            'completada': 'success'
        }
        estado_badge = badge_map.get(ev.estado.lower(), 'secondary')
        #  - progreso: ejemplo sencillo
        if ev.estado.lower() == 'completada':
            progreso = 100
        elif ev.estado.lower() == 'en progreso':
            progreso = 50
        else:
            progreso = 0

        # Serializar parámetros y usuarios para data-app (JSON)
        parametros_serializados = [
            {'id': p.id, 'nombre': p.nombre}
            for p in ev.parametros
        ]
        usuarios_serializados = [
            {'id': u.id, 'nombre': u.nombre_completo}
            for u in ev.usuarios
        ]

        apps_dict[app_obj.id]['evaluaciones'].append({
            'aplicacion_id': app_obj.id,
            'evaluacion_id': ev.id,
            'parametro_nombre': parametro_nombre,
            'estado': ev.estado,
            'estado_badge': estado_badge,
            'progreso': progreso,
            'fecha_inicio': ev.fecha_inicio,
            'fecha_fin': ev.fecha_fin,
            'rondas': ev.rondas,
            'enviada': ev.enviada,
            'comentarios': ev.comentarios or '',
            'parametros': parametros_serializados,
            'usuarios': usuarios_serializados
        })

    # Construir lista de pending_apps para el template
    pending_apps = []
    for data in apps_dict.values():
        app_obj = data['aplicacion_obj']
        pending_apps.append({
            'nombre': app_obj.nombre,
            'aplicacion_id': app_obj.id,
            'evaluaciones': data['evaluaciones']
        })

    # 4. Métricas generales (cards del dashboard)
    total_apps = Aplicacion.query.count()
    completed_apps = Aplicacion.query.filter_by(evaluada=True).count()
    pending_count = total_apps - completed_apps
    app_progress = int((completed_apps / total_apps) * 100) if total_apps else 0
    completed_percent = app_progress
    pending_percent = int((pending_count / total_apps) * 100) if total_apps else 0
    # Por simplicidad, no calculamos un “rating” real
    metrics = {
        'total_apps': total_apps,
        'completed': completed_apps,
        'pending': pending_count,
        'app_progress': app_progress,
        'completed_percent': completed_percent,
        'pending_percent': pending_percent,
        'average_rating': 0,
        'average_percent': 0
    }

    # 5. Todas las evaluaciones (para sección “Resultados – Datos”)
    all_evaluations = []
    evs_all = Evaluacion.query.all()
    for ev in evs_all:
        nombre_app = ev.aplicacion.nombre if ev.aplicacion else '–'
        parametro_nombre = ev.parametros[0].nombre if ev.parametros else '–'
        badge_map = {
            'pendiente': 'warning',
            'en progreso': 'info',
            'completada': 'success'
        }
        estado_badge = badge_map.get(ev.estado.lower(), 'secondary')
        all_evaluations.append({
            'aplicacion_nombre': nombre_app,
            'parametro_nombre': parametro_nombre,
            'estado': ev.estado,
            'estado_badge': estado_badge,
            'fecha_inicio': ev.fecha_inicio,
            'fecha_fin': ev.fecha_fin,
            'rondas': ev.rondas
        })

    # 6. Eventos próximos (para calendario)
    upcoming_events = []
    today = date.today()
    next_month = today + timedelta(days=30)
    evs_upcoming = Evaluacion.query.filter(
        Evaluacion.fecha_inicio >= datetime.combine(today, datetime.min.time()),
        Evaluacion.fecha_inicio <= datetime.combine(next_month, datetime.max.time())
    ).all()
    for ev in evs_upcoming:
        fecha_iso = ev.fecha_inicio.date().isoformat()
        title = f"Evalúa '{ev.aplicacion.nombre}' (Ronda {ev.rondas})"
        upcoming_events.append({'date': fecha_iso, 'title': title})

    return render_template(
        'dashboard/expert_dashboard.html',
        active='dashboard',
        current_user=current_user,
        last_login=last_login,
        form=UpdateAccountForm(),
        notifications=notifications,
        pending_apps=pending_apps,
        metrics=metrics,
        all_evaluations=all_evaluations,
        upcoming_events=upcoming_events,
        now=datetime.utcnow()
    )


@expert_bp.route('/aplicaciones')
@login_required
@expert_required
def aplicaciones():
    # Lista paginada de aplicaciones (para sección “Aplicaciones” si fuera distinta)
    page = request.args.get('page', 1, type=int)
    pagination = Aplicacion.query.paginate(page=page, per_page=9)
    return render_template(
        'dashboard/expert_dashboard.html',
        active='aplicaciones',
        pagination=pagination
    )


@expert_bp.route('/evaluar/<int:app_id>', methods=['GET', 'POST'])
@login_required
@expert_required
def evaluar(app_id):
    app_obj = Aplicacion.query.get_or_404(app_id)
    # Aquí usaríamos un formulario para capturar la evaluación por parámetro/usuario.
    # Dado que tu modelo ResultadoEvaluacion difiere del ejemplo anterior, ajustamos:
    if request.method == 'POST':
        # Obtenemos datos del formulario dinámico (ejemplo sencillo)
        # Suponemos que en el formulario envías: comentario, lista de puntuaciones por parámetro, etc.
        flash('Funcionalidad de evaluar no implementada en este ejemplo.', 'warning')
        return redirect(url_for('expert.dashboard'))

    return render_template('expert_evaluar.html', app=app_obj)


@expert_bp.route('/resultados')
@login_required
@expert_required
def resultados_global():
    # Resultados agregados por aplicación (ejemplo de gráfico o lista)
    results = db.session.query(
        Aplicacion.nombre.label('app_name'),
        db.func.avg(ResultadoEvaluacion.puntuacion_media).label('avg_score'),
        db.func.count(ResultadoEvaluacion.id).label('count')
    ).join(ResultadoEvaluacion, ResultadoEvaluacion.aplicacion_id == Aplicacion.id) \
     .group_by(Aplicacion.id).all()

    return render_template(
        'dashboard/expert_dashboard.html',
        active='resultados',
        results=results
    )


@expert_bp.route('/resultados/<int:app_id>')
@login_required
@expert_required
def resultados(app_id):
    app_obj = Aplicacion.query.get_or_404(app_id)
    resultados_list = ResultadoEvaluacion.query.filter_by(aplicacion_id=app_id).all()
    return render_template(
        'expert_resultados.html',
        app=app_obj,
        resultados_list=resultados_list
    )


@expert_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
@expert_required
def perfil():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.nombre_usuario = form.username.data
        current_user.correo = form.email.data
        db.session.commit()
        flash('Perfil actualizado.', 'success')
        return redirect(url_for('expert.perfil'))

    return render_template(
        'dashboard/expert_dashboard.html',
        active='cuenta',
        form=form
    )


@expert_bp.route('/buscar', methods=['GET'])
@login_required
@expert_required
def buscar_aplicaciones():
    query = request.args.get('q', '', type=str)
    results = Aplicacion.query.filter(Aplicacion.nombre.ilike(f'%{query}%')).all()
    return render_template(
        'dashboard/expert_dashboard.html',
        active='buscar',
        results=results,
        current_user=current_user
    )


# ---------------------------------------------
# Notificaciones
# ---------------------------------------------
@expert_bp.route('/notificaciones')
@login_required
@expert_required
def marcar_notificaciones_leidas():
    # Lógica para marcar notificaciones como leídas
    # (aquí simplemente devolvemos OK; tendrías que actualizar algún campo en BD)
    notificaciones = NotificacionEvaluacion.obtener_notificaciones_leidas(current_user.id)
    for notificacion in notificaciones:
        notificacion.leida = True
    return jsonify({'success': True}), 200


# ---------------------------------------------
# 2) Endpoints AJAX para el dashboard del evaluador
# ---------------------------------------------
@expert_bp.route('/metrics', methods=['GET'])
@login_required
@expert_required
def get_metrics():
    try:
        today = date.today()
        labels = []
        completed_counts = []

        for m in range(5, -1, -1):
            first_of_month = (today.replace(day=1) - timedelta(days=30 * m)).replace(day=1)
            last_of_month = (first_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            month_label = first_of_month.strftime('%b')
            labels.append(month_label)

            count = Evaluacion.query.filter(
                Evaluacion.fecha_inicio >= datetime.combine(first_of_month, datetime.min.time()),
                Evaluacion.fecha_inicio <= datetime.combine(last_of_month, datetime.max.time()),
                Evaluacion.estado == 'completada'
            ).count()
            completed_counts.append(count)

        # Obtener todos los tipos de aplicación y contar cuántas aplicaciones hay de cada tipo
        tipos = TipoAplicacion.query.all()
        platform_labels = [tipo.nombre for tipo in tipos]
        platform_counts = [
            Aplicacion.query.filter(Aplicacion.tipo_aplicacion_id == tipo.id).count()
            for tipo in tipos
        ]

        return jsonify({
            'months': labels,
            'completed_per_month': completed_counts,
            'platforms': platform_labels,
            'by_platform': platform_counts
        }), 200
    except Exception as e:
        print(f"Error en: {e}")
        return jsonify({'error': 'No se pudieron obtener métricas.'}), 500


@expert_bp.route('/events', methods=['GET'])
@login_required
@expert_required
def get_events():
    try:
        today = date.today()
        next_month = today + timedelta(days=30)
        evs = Evaluacion.query.filter(
            Evaluacion.fecha_inicio >= datetime.combine(today, datetime.min.time()),
            Evaluacion.fecha_inicio <= datetime.combine(next_month, datetime.max.time())
        ).all()

        events = []
        for ev in evs:
            fecha = ev.fecha_inicio.date().isoformat()
            title = f"Evalúa '{ev.aplicacion.nombre}' (Ronda {ev.rondas})"
            events.append({'date': fecha, 'title': title})

        return jsonify({'events': events}), 200
    except Exception:
        return jsonify({'error': 'No se pudieron obtener eventos.'}), 500


# ---------------------------------------------
# 3) Actualizar Cuenta (AJAX)
# ---------------------------------------------
@expert_bp.route('/actualizar_cuenta', methods=['POST'])
@login_required
@expert_required
def actualizar_cuenta():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email'):
        return jsonify({'success': False, 'message': 'Datos incompletos.'}), 400
    try:
        current_user.nombre_usuario = data['username']
        current_user.correo = data['email']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cuenta actualizada.'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ---------------------------------------------
# 4) CRUD completo para Evaluaciones (AJAX)
# ---------------------------------------------
@expert_bp.route('/evaluaciones', methods=['GET'])
@login_required
@expert_required
def get_evaluaciones():
    try:
        evs = Evaluacion.query.all()
        return jsonify(success=True, evaluaciones=[e.to_dict() for e in evs]), 200
    except Exception:
        return jsonify(success=False, message='Error al obtener las evaluaciones.'), 500

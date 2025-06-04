# app/routes/expert.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from app.models.aplicacion import Aplicacion
from app.models.resultado import ResultadoEvaluacion
from app.models.evaluacion import Evaluacion, EvaluacionUsuario, EvaluacionParametro, Encuesta
from app.models.usuario import Usuario, NotificacionEvaluacion
from app.extension import db
from app.decorators.expert import expert_required
import datetime

from app.forms.update_account import UpdateAccountForm

expert_bp = Blueprint('expert', __name__, url_prefix='/expert')

# ---------------------------------------------
# 1) Dashboard y páginas principales
# ---------------------------------------------
@expert_bp.route('/dashboard')
@login_required
@expert_required
def dashboard():
    # Estadísticas generales para el evaluador
    stats = {
        'total_apps': Aplicacion.query.count(),
        # 'completed_evals': ResultadoEvaluacion.query.filter_by(user_id=current_user.id).count(),
        # 'pending_evals': Aplicacion.query.count() - ResultadoEvaluacion.query.filter_by(user_id=current_user.id).count(),
        # 'avg_rating': round(db.session.query(db.func.avg(ResultadoEvaluacion.rating)).scalar() or 0, 2)
    }
    
    # metrics = db.session.query(
    #     NotificacionEvaluacion.obtener_aplicaciones_por_usuario(current_user.id).label('total_apps'),
    # ).outerjoin(ResultadoEvaluacion, ResultadoEvaluacion.aplicacion_id == Aplicacion.id).outerjoin(Evaluacion, Evaluacion.aplicacion_id == Aplicacion.id).first()
    
    last_login = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    notifications = NotificacionEvaluacion.obtener_mensajes_por_usuario(current_user.id)
    pending_apps = Evaluacion.obtener_por_aplicacion_y_estado(current_user.id, 'enviado')
    
    return render_template(
        'dashboard/expert_dashboard.html',
        active='dashboard',
        stats=stats,
        last_login=last_login,
        form=UpdateAccountForm(),
        notifications=notifications,
        pending_apps=pending_apps,
        metrics={}
        # metrics={
        #     'total_apps': metrics.total_apps,
        #     'total_evals': metrics.total_evals
        # }
    )

@expert_bp.route('/aplicaciones')
@login_required
@expert_required
def aplicaciones():
    # Lista paginada de aplicaciones
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
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comments = request.form.get('comments')
        if not rating:
            flash('La calificación es requerida.', 'danger')
            return redirect(url_for('expert.evaluar', app_id=app_id))
        eval_obj = ResultadoEvaluacion(
            user_id=current_user.id,
            aplicacion_id=app_id,
            rating=rating,
            comments=comments
        )
        db.session.add(eval_obj)
        db.session.commit()
        flash('Evaluación enviada correctamente.', 'success')
        return redirect(url_for('expert.aplicaciones'))
    return render_template('expert_evaluar.html', app=app_obj)

@expert_bp.route('/resultados')
@login_required
@expert_required
def resultados_global():
    # Resultados agregados por aplicación
    results = db.session.query(
        Aplicacion.nombre.label('app_name'),
        db.func.avg(ResultadoEvaluacion.rating).label('avg_rating'),
        db.func.count(ResultadoEvaluacion.id).label('count')
    ).join(ResultadoEvaluacion).group_by(Aplicacion.id).all()
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
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        if not username or not email:
            flash('Usuario y correo son requeridos.', 'danger')
            return redirect(url_for('expert.perfil'))
        current_user.username = username
        current_user.email = email
        db.session.commit()
        flash('Perfil actualizado.', 'success')
        return redirect(url_for('expert.perfil'))
    return render_template(
        'dashboard/expert_dashboard.html',
        active='cuenta',
        csrf_token=(lambda: (None))()  # el valor real se inyecta en Jinja
    )

@expert_bp.route('/buscar', methods=['GET'])
@login_required
@expert_required
def buscar_aplicaciones():
    query = request.args.get('q', '', type=str)
    results = Aplicacion.query.filter(Aplicacion.nombre.ilike(f'%{query}%')).all()
    return render_template('dashboard/expert_dashboard.html', active='buscar', results=results)


# ---------------------------------------------
# Notificaciones
# ---------------------------------------------
@expert_bp.route('/notificaciones')
@login_required
@expert_required
def marcar_notificaciones_leidas():
    # Lógica para marcar notificaciones como leídas
    return jsonify({'success': True}), 200



# ---------------------------------------------
# 2) Endpoints AJAX para el dashboard del evaluador
# ---------------------------------------------

@expert_bp.route('/metrics', methods=['GET'])
@login_required
@expert_required
def get_metrics():
    """
    Devuelve JSON con:
    - months: ["Ene", "Feb", ...]
    - completed_per_month: [n1, n2, ...]
    - platforms: ["Android", "iOS", "Web"]
    - by_platform: [count_android, count_ios, count_web]
    """
    try:
        today = datetime.date.today()
        labels, completed_counts = [], []
        for m in range(5, -1, -1):
            first = (today.replace(day=1) - datetime.timedelta(days=30*m)).replace(day=1)
            last = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
            month_label = first.strftime('%b')
            labels.append(month_label)

            count = Evaluacion.query.filter(
                Evaluacion.fecha_inicio >= datetime.datetime.combine(first, datetime.time.min),
                Evaluacion.fecha_inicio <= datetime.datetime.combine(last, datetime.time.max),
                Evaluacion.estado == 'completada'
            ).count()
            completed_counts.append(count)

        platforms = ["Android", "iOS", "Web"]
        android_count = Aplicacion.query.filter(Aplicacion.plataforma.ilike("%android%")).count()
        ios_count     = Aplicacion.query.filter(Aplicacion.plataforma.ilike("%ios%")).count()
        web_count     = Aplicacion.query.filter(Aplicacion.plataforma.ilike("%web%")).count()

        return jsonify({
            'months': labels,
            'completed_per_month': completed_counts,
            'platforms': platforms,
            'by_platform': [android_count, ios_count, web_count]
        }), 200
    except Exception:
        return jsonify({'error': 'No se pudieron obtener métricas.'}), 500

@expert_bp.route('/events', methods=['GET'])
@login_required
@expert_required
def get_events():
    """
    Devuelve lista de eventos próximos relacionados con evaluaciones.
    Formato: [{ 'date': 'YYYY-MM-DD', 'title': 'Texto del evento' }, ...]
    """
    try:
        today = datetime.date.today()
        next_month = today + datetime.timedelta(days=30)
        evals = Evaluacion.query.filter(
            Evaluacion.fecha_inicio >= datetime.datetime.combine(today, datetime.time.min),
            Evaluacion.fecha_inicio <= datetime.datetime.combine(next_month, datetime.time.max)
        ).all()

        events = []
        for ev in evals:
            fecha = ev.fecha_inicio.date().isoformat()
            title = f"Evalúa '{ev.aplicacion.nombre}' (Ronda {ev.rondas})"
            events.append({'date': fecha, 'title': title})

        return jsonify({'events': events}), 200
    except Exception:
        return jsonify({'error': 'No se pudieron obtener eventos.'}), 500

# ---------------------------------------------
# Actualizar Cuenta
# ---------------------------------------------
@expert_bp.route('/actualizar_cuenta', methods=['POST'])
@login_required
@expert_required
def actualizar_cuenta():
    """
    Actualiza los datos de la cuenta del evaluador.
    Espera JSON con 'username' y 'email'.
    Devuelve JSON con éxito o error.
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email'):
        return jsonify({'success': False, 'message': 'Datos incompletos.'}), 400
    
    try:
        current_user.username = data['username']
        current_user.email = data['email']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cuenta actualizada.'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ---------------------------------------------
# 3) CRUD completo para Evaluaciones (AJAX)
# ---------------------------------------------

@expert_bp.route('/evaluaciones', methods=['GET'])
@login_required
@expert_required
def get_evaluaciones():
    """
    Devuelve todas las evaluaciones en formato JSON.
    {
      success: True,
      evaluaciones: [ { ...to_dict()... }, ... ]
    }
    """
    try:
        evs = Evaluacion.query.all()
        return jsonify(success=True, evaluaciones=[e.to_dict() for e in evs]), 200
    except Exception:
        return jsonify(success=False, message='Error al obtener las evaluaciones.'), 500
    
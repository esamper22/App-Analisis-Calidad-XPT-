from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models.aplicacion import Aplicacion
from app.models.evaluacion import ResultadoEvaluacion
from app.extension import db

expert_bp = Blueprint('expert', __name__, url_prefix='/expert')

@expert_bp.route('/dashboard')
@login_required
def dashboard():
    # Estadísticas generales para el evaluador
    stats = {
        # 'total_apps': Aplicacion.query.count(),
        # 'completed_evals': ResultadoEvaluacion.query.filter_by(user_id=current_user.id).count(),
        # 'pending_evals': Aplicacion.query.count() - ResultadoEvaluacion.query.filter_by(user_id=current_user.id).count(),
        # 'avg_rating': round(db.session.query(db.func.avg(ResultadoEvaluacion.rating)).scalar() or 0, 2)
    }
    return render_template('dashboard/expert_dashboard.html', active='dashboard', stats=stats)

@expert_bp.route('/aplicaciones')
@login_required
def aplicaciones():
    # Lista paginada de aplicaciones
    page = request.args.get('page', 1, type=int)
    pagination = Aplicacion.query.paginate(page=page, per_page=9)
    return render_template('dashboard/expert_dashboard.html', active='aplicaciones', pagination=pagination)

@expert_bp.route('/evaluar/<int:app_id>')
@login_required
def evaluar(app_id):
    app = Aplicacion.query.get_or_404(app_id)
    # Lógica de presentación del formulario de evaluación
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comments = request.form.get('comments')
        if not rating:
            flash('La calificación es requerida.', 'danger')
            return redirect(url_for('expert.evaluar', app_id=app_id))
        eval_obj = ResultadoEvaluacion(user_id=current_user.id, Aplicacion_id=app_id, rating=rating, comments=comments)
        db.session.add(eval_obj)
        db.session.commit()
        flash('Evaluación enviada correctamente.', 'success')
        return redirect(url_for('expert.aplicaciones'))
    return render_template('expert_evaluar.html', app=app)

@expert_bp.route('/resultados')
@login_required
def resultados_global():
    # Resultados agregados por aplicación
    results = db.session.query(
        Aplicacion.name.label('app_name'),
        db.func.avg(ResultadoEvaluacion.rating).label('avg_rating'),
        db.func.count(ResultadoEvaluacion.id).label('count')
    ).join(ResultadoEvaluacion).group_by(Aplicacion.id).all()
    return render_template('dashboard/expert_dashboard.html', active='resultados', results=results)

@expert_bp.route('/resultados/<int:app_id>')
@login_required
def resultados(app_id):
    app = Aplicacion.query.get_or_404(app_id)
    ResultadoEvaluacions = ResultadoEvaluacion.query.filter_by(Aplicacion_id=app_id).all()
    return render_template('expert_resultados.html', app=app, ResultadoEvaluacions=ResultadoEvaluacions)

@expert_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
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
    return render_template('dashboard/expert_dashboard.html', active='cuenta', csrf_token="{{ csrf_token() }}")

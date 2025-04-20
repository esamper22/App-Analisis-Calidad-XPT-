from flask import Blueprint, render_template

admin_bp = Blueprint('main', __name__)

@admin_bp.route('/')
def index():
    return render_template('landing.html')

@admin_bp.route('/login')
def login_page():
    return render_template('auth/login.html')
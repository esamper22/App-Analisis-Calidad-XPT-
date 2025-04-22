from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('landing.html')

@main_bp.route('/login')
def login_page():
    return render_template('auth/login.html')
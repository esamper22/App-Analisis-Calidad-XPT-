from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db=SQLAlchemy()
migrate=Migrate()
login=LoginManager()

def iniciar_extensiones(app):
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    usuario = StringField(
        'Usuario',
        validators=[DataRequired(message="El usuario es obligatorio"),
                    Length(min=3, max=100)]
    )
    clave = PasswordField(
        'Contraseña',
        validators=[DataRequired(message="La contraseña es obligatoria")]
    )
    recordar = BooleanField('Recordarme')
    enviar = SubmitField('Iniciar Sesión')

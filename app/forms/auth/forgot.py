# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class ForgotPasswordForm(FlaskForm):
    email = StringField('Correo', validators=[
        DataRequired('El correo es obligatorio'),
        Email('Ingrese un correo válido')
    ])
    submit = SubmitField('Enviar enlace')

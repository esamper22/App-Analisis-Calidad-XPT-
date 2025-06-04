from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length

class UpdateAccountForm(FlaskForm):
    username = StringField('Usuario', render_kw={'readonly': True})
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Nueva Contraseña', validators=[Optional(), Length(min=6, message="La contraseña debe tener al menos 6 caracteres.")])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        Optional(),
        EqualTo('password', message='Las contraseñas deben coincidir.')
    ])
    submit = SubmitField('Guardar Cambios')
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class ResetPasswordForm(FlaskForm):
    clave        = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=6)])
    confirmar    = PasswordField('Confirma contraseña',
                       validators=[DataRequired(), EqualTo('clave')])
    submit       = SubmitField('Actualizar contraseña')

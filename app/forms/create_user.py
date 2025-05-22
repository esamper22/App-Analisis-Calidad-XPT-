from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.usuario import Usuario
from app.models.rol import Rol

# Obtener opciones de roles desde el enum Rol
ROLE_CHOICES = [(role.value, role.value.capitalize()) for role in Rol]

class UsuarioForm(FlaskForm):
    csrf_token = HiddenField()  # Flask-WTF gestión automática

    nombre_completo = StringField(
        'Nombre completo',
        validators=[
            DataRequired(message='El nombre completo es obligatorio'),
            Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres')
        ]
    )
    nombre_usuario = StringField(
        'Nombre de usuario',
        validators=[
            DataRequired(message='El nombre de usuario es obligatorio'),
            Length(min=3, max=50, message='El usuario debe tener entre 3 y 50 caracteres')
        ]
    )
    correo = StringField(
        'Correo electrónico',
        validators=[
            DataRequired(message='El correo es obligatorio'),
            Email(message='Formato de correo inválido'),
            Length(max=100)
        ]
    )
    rol = SelectField(
        'Rol',
        choices=[('', 'Seleccionar un rol')] + ROLE_CHOICES,
        validators=[DataRequired(message='El rol es obligatorio')]
    )
    contraseña = PasswordField(
        'Contraseña',
        validators=[
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
        ]
    )
    confirmar_contraseña = PasswordField(
        'Confirmar contraseña',
        validators=[
            EqualTo('contraseña', message='Las contraseñas deben coincidir')
        ]
    )

    def validate_nombre_usuario(self, field):
        # En creación, se valida que no exista
        if not self.meta.csrf:  # Asumimos creación
            if Usuario.query.filter_by(nombre_usuario=field.data).first():
                raise ValidationError('Nombre de usuario ya existe')

    def validate_correo(self, field):
        # Validar unicidad de correo
        if Usuario.query.filter_by(correo=field.data.lower()).first():
            raise ValidationError('Correo ya registrado')

    def validate_rol(self, field):
        # Validar rol dentro del enum
        try:
            Rol(field.data)
        except ValueError:
            raise ValidationError('Rol inválido')

class UsuarioEditForm(FlaskForm):
    nombre_completo = StringField('Nombre completo', validators=[DataRequired(), Length(max=100)])
    nombre_usuario = StringField('Nombre de usuario', validators=[DataRequired(), Length(max=50)])
    correo = StringField('Correo electrónico', validators=[DataRequired(), Email(), Length(max=100)])
    rol = SelectField('Rol', choices=[
        ('admin', 'Admin'),
        ('evaluador', 'Evaluador'),
        ('jefe departamento', 'Jefe Departamento')
    ], validators=[DataRequired()])

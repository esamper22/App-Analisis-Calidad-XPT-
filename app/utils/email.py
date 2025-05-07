# app/email.py
from flask_mail import Message
from flask import url_for, current_app
from app.extension import mail

def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for('main.reset_password', token=token, _external=True)

    msg = Message(
        subject="Restablece tu contraseña",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.correo]
    )
    msg.body = f"""Hola {user.nombre_usuario},

Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para hacerlo:
{reset_url}

Si no fuiste tú, ignora este correo. El enlace expira en 1 hora.

Saludos,
El equipo de tu aplicación
"""
    mail.send(msg)

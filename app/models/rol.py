from enum import Enum

# ------------------------
# Enumeración de Roles
# ------------------------
class Rol(str, Enum):
    USUARIO = "usuario"
    ADMIN = "admin"
    SUPERADMIN = 'superadmin'
    EVALUADOR = "evaluador"
    DESARROLLADOR = "desarrollador"
    INVITADO = "invitado"

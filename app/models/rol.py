from enum import Enum

# ------------------------
# Enumeración de Roles
# ------------------------
class Rol(str, Enum):
    USUARIO = "usuario"
    ADMIN = "admin"
    EVALUADOR = "evaluador"
    DESARROLLADOR = "desarrollador"
    INVITADO = "invitado"

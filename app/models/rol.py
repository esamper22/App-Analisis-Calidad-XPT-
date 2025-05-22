from enum import Enum

# ------------------------
# Enumeración de Roles
# ------------------------
class Rol(str, Enum):
    ADMIN = "admin"
    JEFE_DEPARTAMENTO = 'jefe departamento'
    EVALUADOR = "evaluador"
    

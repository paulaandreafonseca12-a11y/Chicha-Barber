import string
from django.core.exceptions import ValidationError


def validar_password_fuerte(password):
    """
    Reglas mínimas de seguridad para cualquier contraseña del sistema:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un carácter especial
    - Sin espacios (ni al inicio, ni en medio, ni al final)

    Se usa tanto en los formularios (RegistroForm, CrearUsuarioAdminForm)
    como en la vista de cambio de contraseña del perfil, para que la
    regla sea exactamente la misma en todos los lugares.
    """
    errores = []

    if ' ' in password or password != password.strip():
        errores.append("La contraseña no puede contener espacios.")

    if len(password) < 8:
        errores.append("La contraseña debe tener al menos 8 caracteres.")

    if not any(c.isupper() for c in password):
        errores.append("La contraseña debe incluir al menos una letra mayúscula.")

    if not any(c.islower() for c in password):
        errores.append("La contraseña debe incluir al menos una letra minúscula.")

    if not any(c.isdigit() for c in password):
        errores.append("La contraseña debe incluir al menos un número.")

    if not any(c in string.punctuation for c in password):
        errores.append('La contraseña debe incluir al menos un carácter especial (ej: ! @ # $ % & * -).')

    if errores:
        raise ValidationError(errores)
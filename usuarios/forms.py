from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from .models import Usuario, RolUsuario, TipoDocumento
from core.validators import validar_password_fuerte


# ==========================================================
# LÍMITES (se validan SIEMPRE en el servidor)
# ==========================================================

MAX_EMAIL = 30
MAX_NOMBRE = 30
MIN_NOMBRE = 2
MAX_PASSWORD = 15
MAX_PASSWORD_LOGIN = 15
MIN_DOCUMENTO = 6
MAX_DOCUMENTO = 10
MIN_TELEFONO = 7
MAX_TELEFONO = 10
MAX_FOTO_MB = 1


# ==========================================================
# VALIDADORES
# ==========================================================

validador_nombre = RegexValidator(
    regex=r'^[A-Za-zÁÉÍÓÚÜáéíóúüÑñ]+(?:\s[A-Za-zÁÉÍÓÚÜáéíóúüÑñ]+)*$',
    message=(
        'Este campo solo puede contener letras, '
        'sin números, símbolos ni espacios dobles.'
    )
)

validador_solo_numeros = RegexValidator(
    regex=r'^\d+$',
    message='Solo se permiten números, sin espacios ni letras.'
)


def validar_foto(foto):
    """Valida tamaño y tipo SOLO cuando se sube un archivo nuevo."""
    if isinstance(foto, UploadedFile):
        if foto.size > MAX_FOTO_MB * 1024 * 1024:
            raise ValidationError(
                f'La foto no puede superar {MAX_FOTO_MB} MB.'
            )
        tipo = getattr(foto, 'content_type', '') or ''
        if tipo not in ('image/jpeg', 'image/png', 'image/webp'):
            raise ValidationError(
                'Formato no permitido. Usa JPG, PNG o WEBP.'
            )
    return foto


# ==========================================================
# CAMPOS REUTILIZABLES
# ==========================================================

def campo_nombre(label, requerido=True):
    return forms.CharField(
        max_length=MAX_NOMBRE,
        min_length=MIN_NOMBRE,
        required=requerido,
        label=label,
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


def campo_email(placeholder='correo@ejemplo.com'):
    return forms.EmailField(
        max_length=MAX_EMAIL,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': placeholder
        })
    )


def campo_documento():
    return forms.CharField(
        max_length=MAX_DOCUMENTO,
        min_length=MIN_DOCUMENTO,
        label='Número de documento',
        validators=[validador_solo_numeros],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^\d+$',
            'title': f'Solo números (mínimo {MIN_DOCUMENTO} dígitos).'
        })
    )


def campo_telefono():
    return forms.CharField(
        max_length=MAX_TELEFONO,
        min_length=MIN_TELEFONO,
        label='Teléfono',
        validators=[validador_solo_numeros],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^\d+$'
        })
    )


def campo_tipo_documento():
    return forms.ChoiceField(
        choices=TipoDocumento.choices,
        label='Tipo de documento',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


def campo_rol():
    return forms.ChoiceField(
        choices=RolUsuario.choices,
        label='Rol',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


def campo_foto():
    return forms.ImageField(
        required=False,
        label='Foto de perfil',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )


# ==========================================================
# MIXINS DE VALIDACIÓN (backend)
# ==========================================================

class ValidacionUsuarioMixin:
    """
    Validaciones comunes de correo, documento y foto.
    Funciona para crear (instance.pk = None) y para editar
    (excluye al propio usuario de la búsqueda de duplicados).
    """

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        if len(email) > MAX_EMAIL:
            raise ValidationError(
                f'El correo no puede superar {MAX_EMAIL} caracteres.'
            )

        qs = Usuario.objects.filter(email__iexact=email)

        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError(
                'Ya existe una cuenta registrada con este correo electrónico.'
            )

        return email

    def clean_numero_documento(self):
        numero = self.cleaned_data.get('numero_documento', '').strip()

        qs = Usuario.objects.filter(numero_documento=numero)

        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError(
                'Ya existe un usuario con este número de documento.'
            )

        return numero

    def clean_foto_perfil(self):
        return validar_foto(self.cleaned_data.get('foto_perfil'))


class PasswordFuerteMixin:
    """Longitud máxima + reglas de contraseña fuerte."""

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if password:
            if len(password) > MAX_PASSWORD:
                raise ValidationError(
                    f'La contraseña no puede superar {MAX_PASSWORD} caracteres.'
                )
            validar_password_fuerte(password)

        return password


# ==========================================================
# FORMULARIO DE REGISTRO
# ==========================================================

class RegistroForm(
    ValidacionUsuarioMixin,
    PasswordFuerteMixin,
    UserCreationForm
):

    tipo_documento = campo_tipo_documento()
    numero_documento = campo_documento()
    primer_nombre = campo_nombre('Primer nombre')
    segundo_nombre = campo_nombre('Segundo nombre', requerido=False)
    primer_apellido = campo_nombre('Primer apellido')
    segundo_apellido = campo_nombre('Segundo apellido', requerido=False)
    email = campo_email()
    telefono = campo_telefono()

    # Descomenta esta línea SOLO si tu plantilla registro.html tiene
    # un checkbox con name="acepta_terminos"; si no, el registro
    # fallaría porque el campo es obligatorio.
    #
    # acepta_terminos = forms.BooleanField(
    #     required=True,
    #     error_messages={
    #         'required': 'Debes aceptar los términos y condiciones.'
    #     },
    # )

    class Meta:
        model = Usuario

        fields = (
            'tipo_documento',
            'numero_documento',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'email',
            'telefono',
            'password1',
            'password2',
        )


# ==========================================================
# LOGIN
# ==========================================================

class CustomLoginForm(AuthenticationForm):

    username = forms.EmailField(
        max_length=MAX_EMAIL,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'oninput': (
                "this.value = this.value.toLowerCase()"
                ".replace(/\\s/g, '')"
            )
        })
    )

    password = forms.CharField(
        max_length=MAX_PASSWORD_LOGIN,
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        })
    )

    def clean_username(self):
        return self.cleaned_data.get(
            'username',
            ''
        ).strip().lower()


# ==========================================================
# CREAR USUARIO DESDE ADMIN
# ==========================================================

class CrearUsuarioAdminForm(
    ValidacionUsuarioMixin,
    PasswordFuerteMixin,
    UserCreationForm
):

    numero_documento = campo_documento()
    email = campo_email()
    tipo_documento = campo_tipo_documento()
    primer_nombre = campo_nombre('Primer nombre')
    segundo_nombre = campo_nombre('Segundo nombre', requerido=False)
    primer_apellido = campo_nombre('Primer apellido')
    segundo_apellido = campo_nombre('Segundo apellido', requerido=False)
    telefono = campo_telefono()
    foto_perfil = campo_foto()
    rol = campo_rol()

    estado = forms.BooleanField(
        required=False,
        initial=True,
        label='Usuario activo',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Usuario

        fields = (
            'numero_documento',
            'email',
            'tipo_documento',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'telefono',
            'foto_perfil',
            'rol',
            'estado',
            'password1',
            'password2',
        )

    def save(self, commit=True):

        usuario = super().save(commit=False)

        usuario.email = self.cleaned_data['email'].strip().lower()
        usuario.estado = self.cleaned_data.get('estado', True)

        if commit:
            usuario.save()

        return usuario


# ==========================================================
# EDITAR USUARIO
# ==========================================================

class EditarUsuarioForm(ValidacionUsuarioMixin, forms.ModelForm):

    primer_nombre = campo_nombre('Primer nombre')
    segundo_nombre = campo_nombre('Segundo nombre', requerido=False)
    primer_apellido = campo_nombre('Primer apellido')
    segundo_apellido = campo_nombre('Segundo apellido', requerido=False)
    telefono = campo_telefono()
    email = campo_email(placeholder='')
    tipo_documento = campo_tipo_documento()
    numero_documento = campo_documento()
    rol = campo_rol()
    foto_perfil = campo_foto()

    estado = forms.BooleanField(
        required=False,
        label='Usuario activo',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Usuario

        fields = (
            'tipo_documento',
            'numero_documento',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'email',
            'telefono',
            'rol',
            'estado',
            'foto_perfil',
        )


# ==========================================================
# EDITAR PERFIL
# ==========================================================

class EditarPerfilForm(ValidacionUsuarioMixin, forms.ModelForm):

    primer_nombre = campo_nombre('Primer nombre')
    segundo_nombre = campo_nombre('Segundo nombre', requerido=False)
    primer_apellido = campo_nombre('Primer apellido')
    segundo_apellido = campo_nombre('Segundo apellido', requerido=False)
    telefono = campo_telefono()
    numero_documento = campo_documento()
    tipo_documento = campo_tipo_documento()
    email = campo_email(placeholder='Correo electrónico')
    foto_perfil = campo_foto()

    class Meta:
        model = Usuario

        fields = [
            'tipo_documento',
            'numero_documento',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'telefono',
            'email',
            'foto_perfil',
        ]


# ==========================================================
# RECUPERACIÓN DE CONTRASEÑA
# ==========================================================

class RecuperarPasswordForm(forms.Form):

    email = forms.EmailField(
        max_length=MAX_EMAIL,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu correo registrado',
            'oninput': (
                "this.value = this.value.toLowerCase()"
                ".replace(/\\s/g, '')"
            )
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        if not Usuario.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                'No existe ninguna cuenta registrada con este correo electrónico.'
            )

        return email
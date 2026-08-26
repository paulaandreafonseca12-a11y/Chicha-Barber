from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from .models import Usuario, RolUsuario, TipoDocumento
from core.validators import validar_password_fuerte


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


# ==========================================================
# FORMULARIO DE REGISTRO
# ==========================================================

class RegistroForm(UserCreationForm):

    numero_documento = forms.CharField(
        max_length=20,
        min_length=6,
        label='Número de documento',
        validators=[validador_solo_numeros],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^\d+$',
            'title': 'Solo se permiten números.'
        })
    )

    primer_nombre = forms.CharField(
        max_length=150,
        label='Primer nombre',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    segundo_nombre = forms.CharField(
        max_length=150,
        required=False,
        label='Segundo nombre',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    primer_apellido = forms.CharField(
        max_length=150,
        label='Primer apellido',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    segundo_apellido = forms.CharField(
        max_length=150,
        required=False,
        label='Segundo apellido',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    tipo_documento = forms.ChoiceField(
        choices=TipoDocumento.choices,
        label='Tipo de documento',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )

    telefono = forms.CharField(
        max_length=15,
        min_length=7,
        label='Teléfono',
        validators=[validador_solo_numeros],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^\d+$'
        })
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
            'password1',
            'password2',
        )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        if Usuario.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                'Ya existe una cuenta registrada con este correo electrónico.'
            )

        return email

    def clean_numero_documento(self):
        numero = self.cleaned_data.get(
            'numero_documento',
            ''
        ).strip()

        if Usuario.objects.filter(
            numero_documento=numero
        ).exists():
            raise ValidationError(
                'Ya existe una cuenta registrada con este número de documento.'
            )

        return numero

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if password:
            validar_password_fuerte(password)

        return password


# ==========================================================
# LOGIN
# ==========================================================

class CustomLoginForm(AuthenticationForm):

    username = forms.EmailField(
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

class CrearUsuarioAdminForm(UserCreationForm):

    numero_documento = forms.CharField(
        max_length=20,
        min_length=6,
        label='Número de documento',
        validators=[validador_solo_numeros],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^\d+$'
        })
    )

    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )

    tipo_documento = forms.ChoiceField(
        choices=TipoDocumento.choices,
        label='Tipo de documento',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    primer_nombre = forms.CharField(
        max_length=150,
        label='Primer nombre',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    segundo_nombre = forms.CharField(
        max_length=150,
        required=False,
        label='Segundo nombre',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    primer_apellido = forms.CharField(
        max_length=150,
        label='Primer apellido',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    segundo_apellido = forms.CharField(
        max_length=150,
        required=False,
        label='Segundo apellido',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    telefono = forms.CharField(
        max_length=15,
        min_length=7,
        label='Teléfono',
        validators=[validador_solo_numeros],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^\d+$'
        })
    )

    foto_perfil = forms.ImageField(
        required=False,
        label='Foto de perfil',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )

    rol = forms.ChoiceField(
        choices=RolUsuario.choices,
        label='Rol',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    estado = forms.BooleanField(
        required=False,
        initial=True,
        label='Usuario activo',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
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

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        if Usuario.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                'Ya existe una cuenta registrada con este correo electrónico.'
            )

        return email

    def clean_numero_documento(self):
        numero = self.cleaned_data.get(
            'numero_documento',
            ''
        ).strip()

        if Usuario.objects.filter(
            numero_documento=numero
        ).exists():
            raise ValidationError(
                'Ya existe una cuenta registrada con este número de documento.'
            )

        return numero

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if password:
            validar_password_fuerte(password)

        return password

    def save(self, commit=True):

        usuario = super().save(commit=False)

        usuario.email = self.cleaned_data[
            'email'
        ].strip().lower()

        usuario.estado = self.cleaned_data.get(
            'estado',
            True
        )

        if commit:
            usuario.save()

        return usuario


# ==========================================================
# EDITAR USUARIO
# ==========================================================

class EditarUsuarioForm(forms.ModelForm):

    primer_nombre = forms.CharField(
        max_length=150,
        label='Primer nombre',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    segundo_nombre = forms.CharField(
        max_length=150,
        required=False,
        label='Segundo nombre',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    primer_apellido = forms.CharField(
        max_length=150,
        label='Primer apellido',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    segundo_apellido = forms.CharField(
        max_length=150,
        required=False,
        label='Segundo apellido',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    telefono = forms.CharField(
        max_length=15,
        min_length=7,
        label='Teléfono',
        validators=[validador_solo_numeros],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^\d+$'
        })
    )

    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )

    tipo_documento = forms.ChoiceField(
        choices=TipoDocumento.choices,
        label='Tipo de documento',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    numero_documento = forms.CharField(
        max_length=20,
        label='Número de documento',
        validators=[validador_solo_numeros],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    rol = forms.ChoiceField(
        choices=RolUsuario.choices,
        label='Rol',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    estado = forms.BooleanField(
        required=False,
        label='Usuario activo',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    foto_perfil = forms.ImageField(
        required=False,
        label='Foto de perfil',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
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

    def clean_email(self):
        email = self.cleaned_data.get(
            'email',
            ''
        ).strip().lower()

        qs = Usuario.objects.filter(
            email__iexact=email
        )

        if self.instance and self.instance.pk:
            qs = qs.exclude(
                pk=self.instance.pk
            )

        if qs.exists():
            raise ValidationError(
                'Ya existe otra cuenta registrada con este correo electrónico.'
            )

        return email

    def clean_numero_documento(self):
        numero = self.cleaned_data.get(
            'numero_documento',
            ''
        ).strip()

        qs = Usuario.objects.filter(
            numero_documento=numero
        )

        if self.instance and self.instance.pk:
            qs = qs.exclude(
                pk=self.instance.pk
            )

        if qs.exists():
            raise ValidationError(
                'Ya existe otro usuario con este número de documento.'
            )

        return numero


# ==========================================================
# EDITAR PERFIL
# ==========================================================

class EditarPerfilForm(forms.ModelForm):

    primer_nombre = forms.CharField(
        max_length=150,
        label='Primer nombre',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    segundo_nombre = forms.CharField(
        max_length=150,
        required=False,
        label='Segundo nombre',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    primer_apellido = forms.CharField(
        max_length=150,
        label='Primer apellido',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    segundo_apellido = forms.CharField(
        max_length=150,
        required=False,
        label='Segundo apellido',
        validators=[validador_nombre],
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    telefono = forms.CharField(
        max_length=15,
        min_length=7,
        label='Teléfono',
        validators=[validador_solo_numeros],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^\d+$'
        })
    )

    tipo_documento = forms.ChoiceField(
        choices=TipoDocumento.choices,
        label='Tipo de documento',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

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

        widgets = {
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico'
            }),

            'foto_perfil': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get(
            'email',
            ''
        ).strip().lower()

        qs = Usuario.objects.filter(
            email__iexact=email
        )

        if self.instance and self.instance.pk:
            qs = qs.exclude(
                pk=self.instance.pk
            )

        if qs.exists():
            raise ValidationError(
                'Ya existe otra cuenta registrada con este correo electrónico.'
            )

        return email


# ==========================================================
# RECUPERACIÓN DE CONTRASEÑA
# ==========================================================

class RecuperarPasswordForm(forms.Form):

    email = forms.EmailField(
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
        email = self.cleaned_data.get(
            'email',
            ''
        ).strip().lower()

        if not Usuario.objects.filter(
            email__iexact=email
        ).exists():
            raise ValidationError(
                'No existe ninguna cuenta registrada con este correo electrónico.'
            )

        return email
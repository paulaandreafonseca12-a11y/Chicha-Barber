from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario
from django.core.validators import RegexValidator
from .models import Usuario, ROLES

class RegistroForm(UserCreationForm):

    username = forms.CharField(
        max_length=20,
        label="Número de Documento",
        validators=[RegexValidator(r'^\d+$', 'Solo números')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    telefono = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d+$', 'Solo números')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario

        # 🔥 IMPORTANTE: rol ELIMINADO
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'telefono',
            'password1',
            'password2'
        )


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
class CrearUsuarioAdminForm(UserCreationForm):

    username = forms.CharField(
        max_length=20,
        label="Número de Documento",
        validators=[RegexValidator(r'^\d+$', 'Solo números')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    first_name = forms.CharField(
        max_length=150,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        max_length=150,
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    telefono = forms.CharField(
        max_length=15,
        label="Teléfono",
        validators=[RegexValidator(r'^\d+$', 'Solo números')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    ROL_CHOICES = [
        ('cliente', 'Cliente'),
        ('barbero', 'Barbero'),
        ('admin', 'Administrador'),
    ]

    rol = forms.ChoiceField(
        choices=ROL_CHOICES,
        label="Rol",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    is_staff = forms.BooleanField(
        required=False,
        label="Acceso al panel admin",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Usuario
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'telefono', 'rol', 'is_staff',
            'password1', 'password2'
        )
        
class EditarUsuarioForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=150,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        max_length=150,
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    telefono = forms.CharField(
        max_length=15,
        label="Teléfono",
        validators=[RegexValidator(r'^\d+$', 'Solo números')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    rol = forms.ChoiceField(
        choices=ROLES,
        label="Rol",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    is_staff = forms.BooleanField(
        required=False,
        label="Acceso al panel admin",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    estado = forms.BooleanField(
        required=False,
        label="Usuario activo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 'rol', 'is_staff', 'estado')
        
class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'telefono', 'email', 'foto_perfil']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre(s)'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido(s)'}),
            'telefono':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'foto_perfil': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
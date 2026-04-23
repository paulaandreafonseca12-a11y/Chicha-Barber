from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re

ROLES_REGISTRO = (
    ('cliente', 'Cliente'),
    ('barbero', 'Barbero'),
)

class RegistroForm(UserCreationForm):
    username = forms.CharField(
        max_length=20,
        label="Número de Documento",
        validators=[RegexValidator(r'^\d+$', 'El documento solo debe contener números.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 1000123456'})
    )
    first_name = forms.CharField(
        max_length=150,
        label="Nombre(s)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Juan'})
    )
    last_name = forms.CharField(
        max_length=150,
        label="Apellido(s)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Pérez'})
    )
    telefono = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d+$', 'El teléfono solo debe contener números.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300 123 4567'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    rol = forms.ChoiceField(
        choices=ROLES_REGISTRO,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'rol')

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Tu contraseña'})
    )
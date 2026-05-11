from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario
from django.core.validators import RegexValidator


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
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario 
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re

class RegistroForm(UserCreationForm):
    nombre_completo = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre completo'})
    )
    
    # Validación: Solo números para el teléfono
    telefono = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d+$', 'El teléfono solo debe contener números.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300 123 4567'})
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )

    class Meta:
        model = Usuario
        # El username se manejará internamente en la vista usando el email
        fields = ('nombre_completo', 'email', 'telefono')

    # VALIDACIÓN DE CONTRASEÑA SEGURA
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("La contraseña debe contener al menos una mayúscula.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("La contraseña debe contener al menos una minúscula.")
        if not re.search(r'[0-9]', password):
            raise ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("La contraseña debe contener al menos un carácter especial (!@#$%^&*...).")
            
        return password
import re

from django import forms
from django.forms import ModelForm
from .models import Servicios, Calificacion


class ValidacionServicioMixin:
    nombre_pattern = r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s&+().,'/-]+$"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].error_messages.update({
            'required': 'Ingrese el nombre del servicio.',
            'invalid': 'Use solo letras y espacios; el nombre no admite números.',
            'max_length': 'El nombre del servicio no puede superar 150 caracteres.',
        })
        self.fields['precio'].error_messages.update({
            'required': 'Ingrese el precio usando solo números.',
            'invalid': 'El precio debe contener solo números.',
            'max_digits': 'El precio admite máximo 10 dígitos y 2 decimales.',
            'max_decimal_places': 'El precio admite máximo 2 decimales.',
            'max_whole_digits': 'El precio admite máximo 8 dígitos enteros.',
        })
        self.fields['duracion'].error_messages.update({
            'required': 'Ingrese la duración en minutos usando solo números.',
            'invalid': 'La duración debe ser un número entero.',
        })
        self.fields['descripcion'].error_messages.update({
            'required': 'Ingrese una descripción para el servicio.',
        })
        self.fields['imagen'].error_messages.update({
            'invalid_image': 'Seleccione un archivo de imagen válido.',
        })

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 2:
            raise forms.ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )
        if any(caracter.isdigit() for caracter in nombre):
            raise forms.ValidationError(
                'El nombre no puede contener números; escriba solo letras.'
            )
        if not re.fullmatch(self.nombre_pattern, nombre):
            raise forms.ValidationError(
                'El nombre contiene caracteres no permitidos.'
            )
        return nombre

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        return precio

    def clean_duracion(self):
        duracion = self.cleaned_data.get('duracion')
        if duracion is not None and duracion < 1:
            raise forms.ValidationError(
                'La duración debe ser de al menos un minuto.'
            )
        return duracion

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '').strip()
        if len(descripcion) < 10:
            raise forms.ValidationError(
                'La descripción debe tener al menos 10 caracteres.'
            )
        return descripcion


class ServiciosForm(ValidacionServicioMixin, ModelForm):
    class Meta:
        model = Servicios
        fields = ['nombre', 'precio', 'duracion', 'descripcion', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Corte de cabello',
                'pattern': ValidacionServicioMixin.nombre_pattern,
                'title': 'Use solo letras y espacios; no ingrese números.',
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'inputmode': 'decimal',
                'title': 'Ingrese solo números. El precio no puede ser negativo.',
            }),
            'duracion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1',
                'inputmode': 'numeric',
                'title': 'La duración debe ser de al menos un minuto.',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ServiciosEditarForm(ValidacionServicioMixin, ModelForm):
    class Meta:
        model = Servicios
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': ValidacionServicioMixin.nombre_pattern,
                'title': 'Use solo letras y espacios; no ingrese números.',
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'inputmode': 'decimal',
                'title': 'Ingrese solo números. El precio no puede ser negativo.',
            }),
            'duracion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1',
                'inputmode': 'numeric',
                'title': 'Ingrese solo números enteros (mínimo 1 minuto).',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'estado': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class CalificacionForm(ModelForm):
    cliente_nombre = forms.CharField(
        label='Tu nombre',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'name',
            'pattern': r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s'-]+$",
            'title': 'Use solo letras, espacios, guiones o apóstrofos; no ingrese números.',
        }),
    )

    class Meta:
        model = Calificacion
        fields = ['servicio', 'cliente_nombre', 'puntuacion', 'comentario']
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'puntuacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1,
                'inputmode': 'numeric',
                'title': 'Ingrese solo números enteros del 1 al 5.',
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': 1000,
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['servicio'].queryset = Servicios.objects.filter(
            estado=True
        ).order_by('nombre')
        self.fields['servicio'].error_messages.update({
            'required': 'Seleccione un servicio.',
            'invalid_choice': 'Seleccione un servicio válido.',
        })
        self.fields['puntuacion'].error_messages.update({
            'required': 'Ingrese una puntuación del 1 al 5.',
            'invalid': 'La puntuación debe ser un número entero del 1 al 5.',
            'min_value': 'La puntuación mínima es 1.',
            'max_value': 'La puntuación máxima es 5.',
        })
        self.fields['comentario'].error_messages.update({
            'required': 'Ingrese un comentario.',
        })
        if user is not None and user.is_authenticated:
            self.fields.pop('cliente_nombre')
        else:
            self.fields['cliente_nombre'].error_messages.update({
                'required': 'Ingrese su nombre usando solo letras.',
                    'max_length': 'El nombre no puede superar 150 caracteres.',
            })

    def clean_cliente_nombre(self):
        nombre = self.cleaned_data['cliente_nombre'].strip()
        if len(nombre) < 2:
            raise forms.ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )
        if any(caracter.isdigit() for caracter in nombre):
            raise forms.ValidationError(
                'El nombre no puede contener números; escriba solo letras.'
            )
        if not all(
            caracter.isalpha() or caracter.isspace() or caracter in "'-"
            for caracter in nombre
        ):
            raise forms.ValidationError(
                'Use solo letras, espacios, guiones o apóstrofos en el nombre.'
            )
        return nombre

    def clean_comentario(self):
        comentario = self.cleaned_data['comentario'].strip()
        if len(comentario) < 10:
            raise forms.ValidationError(
                'El comentario debe tener al menos 10 caracteres.'
            )
        if len(comentario) > 1000:
            raise forms.ValidationError(
                'El comentario no puede superar 1000 caracteres.'
            )
        return comentario

    def clean_puntuacion(self):
        puntuacion = self.cleaned_data['puntuacion']
        if not 1 <= puntuacion <= 5:
            raise forms.ValidationError(
                'La puntuación debe ser un número del 1 al 5.'
            )
        return puntuacion

class ResponderCalificacionForm(forms.Form):
    respuesta = forms.CharField(
        label='Escribe tu respuesta',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe aquí tu respuesta al cliente...'}),
        required=True
        
    )
    
    

                
    
    


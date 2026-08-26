from django import forms # type: ignore
from django.forms import ModelForm # type: ignore
from django.contrib.admin.widgets import FilteredSelectMultiple # type: ignore
from .models import  Promocion

class PromocionForm(ModelForm):
    class Meta:
        model = Promocion
        fields=['servicio', 'nombre', 'porcentaje_descuento', 'duracion', 'descripcion', 'imagen',]
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Promocion Verano',
                'pattern': r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$',
                'title': 'El nombre solo puede contener letras, números y espacios.'
            }),
            
            'porcentaje_descuento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50,
                'pattern': r'^[0-9]+$',
                'title': 'El porcentaje solo puede contener números.'
            }),
            
            'duracion': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 30 días',
                'pattern': r'^[0-9]+$',
                'title': 'La duración solo puede contener números.'
            }),
           
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la promoción',
                'pattern': r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$',
                'title': 'La descripción solo puede contener letras y ser msayor a 10 caracteres.'
            }),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
    def clean_porcentaje_descuento(self):
        porcentaje = self.cleaned_data.get('porcentaje_descuento')
        if porcentaje is not None and (porcentaje < 0 or porcentaje > 50):
            raise forms.ValidationError("El porcentaje de descuento debe estar entre 0 y 50.")
        return porcentaje

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion and len(descripcion) < 10:
            raise forms.ValidationError("La descripción debe tener al menos 10 caracteres.")
        return descripcion
    
    def clean_duracion(self):
        duracion = self.cleaned_data.get('duracion')
        if duracion and not duracion.isdigit():
            raise forms.ValidationError("La duración debe ser un número.")
        return duracion
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre and not all(char.isalpha() or char.isspace() for char in nombre):
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")
        return nombre

class PromocionEditarForm(ModelForm):
    class Meta:
        model = Promocion
        fields = '__all__'
        


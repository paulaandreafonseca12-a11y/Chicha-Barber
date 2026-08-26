from django import forms # type: ignore
from django.forms import ModelForm # type: ignore
from django.contrib.admin.widgets import FilteredSelectMultiple # type: ignore
from .models import Servicios, Calificacion



class ServiciosForm(ModelForm):
    class Meta:
        model = Servicios
        fields=['nombre', 'precio', 'duracion','imagen', ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Corte de cabello',
                'pattern': r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\]+$',
                'title': 'El nombre solo puede contener letras, números y espacios.'
            }),
            
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'title': 'El precio debe ser un número positivo.'
            }),
            
            'duracion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'title': 'La duración debe ser un número positivo.'
            }),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
        def clean_precio(self):
            precio = self.cleaned_data.get('precio')
            if precio is not None and precio < 0:
                raise forms.ValidationError("El precio debe ser un número positivo.")
            return precio
        
        def clean_nombre(self):
            nombre = self.cleaned_data.get('nombre')
            if nombre and not all(char.isalpha() or char.isspace() for char in nombre):
                raise forms.ValidationError("El nombre solo puede contener letras y espacios.")
            return nombre
        
        def clean_duracion(self):
            duracion = self.cleaned_data.get('duracion')
            if duracion is not None and duracion < 1:
                raise forms.ValidationError("La duración debe ser un número positivo.")
            return duracion
        
class ServiciosEditarForm(ModelForm):
    class Meta:
        model = Servicios
        fields = '__all__'
        
class CalificacionForm(ModelForm):
    class Meta:
        model = Calificacion
        # Se quita 'cliente' — ahora se asigna automáticamente
        # en la vista con request.user, no lo llena el usuario a mano.
        fields = ['servicio', 'puntuacion', 'comentario']
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'puntuacion': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
           
        }

        
        

class ResponderCalificacionForm(forms.Form):
    respuesta = forms.CharField(
        label='Escribe tu respuesta',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe aquí tu respuesta al cliente...'}),
        required=True
        
    )
    
    



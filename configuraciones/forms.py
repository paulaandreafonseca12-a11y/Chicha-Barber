from django import forms
from .models import Carrusel

class CarruselForm(forms.ModelForm):
    class Meta:
        model = Carrusel
        fields = ['nombre', 'imagen', 'texto', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'imagen': 'Tamaño recomendado: 1200x500 píxeles. La imagen se redimensionará automáticamente a estas dimensiones si es de otro tamaño.',
        }

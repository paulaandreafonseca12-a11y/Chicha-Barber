from django import forms
from .models import Carrusel

class CarruselForm(forms.ModelForm):
    class Meta:
        model = Carrusel
        fields = ['nombre', 'imagen', 'texto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
        }
        help_texts = {
            'imagen': 'Tamaño recomendado: 1200x500 píxeles. La imagen se redimensionará automáticamente a estas dimensiones si es de otro tamaño.',
            'texto': 'Descripción obligatoria para accesibilidad y SEO.',
        }

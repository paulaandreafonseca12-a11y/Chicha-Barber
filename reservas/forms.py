from django import forms
from .models import Reserva, Calificacion

# --- FORMULARIOS DE RESERVAS ---
class ReservaForm(forms.ModelForm):
    fecha = forms.CharField(required=True)
    hora = forms.CharField(required=True)

    class Meta:
        model = Reserva
        fields = '__all__'
        exclude = ['fecha_reserva', 'servicio']

class ReservaFormCompleto(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['nombre_cliente', 'correo_cliente', 'telefono_cliente', 'fecha_reserva', 'servicio']

# --- FORMULARIOS DE CALIFICACIONES ---
class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        # Solo puntuación y reseña, como pediste
        fields = ['puntuacion', 'resena']
        widgets = {
            'resena': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Cuéntanos tu experiencia...'
            }),
            'puntuacion': forms.HiddenInput(),
        }

class CalificacionEditarForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['puntuacion', 'resena']

class ReservaEditarForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['nombre_cliente', 'correo_cliente', 'telefono_cliente', 'fecha_reserva', 'estado']
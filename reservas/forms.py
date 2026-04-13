from django import forms
from .models import Reserva, Calificacion
from usuarios.models import Barbero

# reservas/forms.py
class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['nombre_cliente', 'correo_cliente', 'telefono_cliente', 'fecha_reserva', 'servicio']
        
class EditarReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        # Usamos telefono_cliente y correo_cliente para que Django no lance FieldError
        fields = ['nombre_cliente', 'correo_cliente', 'telefono_cliente', 'fecha_reserva', 'estado']

class CalificacionForm(forms.ModelForm):
    barbero_a_calificar = forms.ModelChoiceField(
        queryset=Barbero.objects.all(),
        empty_label="Selecciona a tu barbero...",
        required=True,
        widget=forms.Select(attrs={'class': 'select-barbero'})
    )

    class Meta:
        model = Calificacion
        fields = ['barbero_a_calificar', 'calificacion', 'resenia']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Esto te ayudará a ver en la terminal si los barberos cargan bien
        print(f"DEBUG: Barberos encontrados: {Barbero.objects.count()}")

class CalificacionEditarForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = '__all__'

# Agregamos esta por si tus views la llaman con este nombre
class ReservaEditarForm(EditarReservaForm):
    pass
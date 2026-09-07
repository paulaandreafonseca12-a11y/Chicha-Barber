from django import forms
from .models import Reserva

# --- FORMULARIOS DE RESERVAS ---
class ReservaForm(forms.ModelForm):
    fecha = forms.CharField(required=True)
    hora = forms.CharField(required=True)

    class Meta:
        model = Reserva
        # Se especifican explícitamente los campos del modelo que se van a exponer.
        # Esto evita exponer campos internos como 'estado' de forma accidental.
        fields = ['telefono_usuario', 'observacion']

class ReservaFormCompleto(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['telefono_usuario', 'observacion', 'fecha_reserva', 'servicio']

class ReservaEditarForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['telefono_usuario', 'observacion', 'fecha_reserva', 'estado']
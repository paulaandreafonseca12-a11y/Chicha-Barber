from django import forms
from .models import Reserva

# --- FORMULARIOS DE RESERVAS ---
class ReservaForm(forms.ModelForm):
    # Campos adicionales que no pertenecen directamente al modelo pero se usan en el formulario
    fecha = forms.CharField(required=True)
    hora = forms.CharField(required=True)

    class Meta:
        model = Reserva
        # Se especifican explícitamente los campos del modelo que se van a exponer.
        # Esto evita exponer campos internos como 'estado' de forma accidental.
        fields = ['nombre_cliente', 'correo_cliente', 'telefono_cliente']

class ReservaFormCompleto(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['nombre_cliente', 'correo_cliente', 'telefono_cliente', 'fecha_reserva', 'servicio']

class ReservaEditarForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['nombre_cliente', 'correo_cliente', 'telefono_cliente', 'fecha_reserva', 'estado']
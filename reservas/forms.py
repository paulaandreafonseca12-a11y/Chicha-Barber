from django import forms
from .models import Reserva
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



class ReservaEditarForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['nombre_cliente', 'correo_cliente', 'telefono_cliente', 'fecha_reserva', 'estado']
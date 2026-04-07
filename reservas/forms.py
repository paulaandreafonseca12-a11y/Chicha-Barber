from django import forms
from .models import Reserva, Calificacion
from usuarios.models import Barbero

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = '__all__'

class ReservaEditarForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = '__all__'

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
        # Esto imprimirá el conteo en tu terminal de VS Code
        print(f"DEBUG: Barberos encontrados en el formulario: {Barbero.objects.count()}")

# ESTA ES LA CLASE QUE FALTA Y ESTÁ ROMPIENDO TU PROYECTO
class CalificacionEditarForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = '__all__'
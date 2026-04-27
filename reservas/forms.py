from django import forms

from usuarios.models import Usuario
from .models import Reserva, Calificacion

from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    # Definimos estos campos para que Django los acepte en el POST
    fecha = forms.CharField(required=True)
    hora = forms.CharField(required=True)

    class Meta:
        model = Reserva
        fields = '__all__'
        # Quitamos fecha_reserva y servicio de la validación obligatoria del form
        # porque los construiremos manualmente en la vista.
        exclude = ['fecha_reserva', 'servicio']

<<<<<<< Updated upstream
class EditarReservaForm(forms.ModelForm):
=======
class ReservaFormCompleto(forms.ModelForm):
>>>>>>> Stashed changes
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
        queryset=Usuario.objects.filter(rol='barbero').order_by('username'),
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
        print(f"DEBUG: Barberos encontrados: {Usuario.objects.filter(rol='barbero').count()}")

class CalificacionEditarForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = '__all__'

# Agregamos esta por si tus views la llaman con este nombre
class ReservaEditarForm(EditarReservaForm):
    pass
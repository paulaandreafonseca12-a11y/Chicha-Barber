from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple
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
class ReservaEditarForm(ModelForm):
    class Meta:
        model = Reserva
        fields = '__all__'

class CalificacionForm(ModelForm):
    class Meta:
        model = Calificacion
        fields = '__all__'

class CalificacionEditarForm(ModelForm):
    class Meta:
        model = Calificacion
        fields = '__all__'
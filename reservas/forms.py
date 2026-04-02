from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Reserva, Calificacion

class ReservaForm(ModelForm):
    class Meta:
        model = Reserva
        fields = '__all__'
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
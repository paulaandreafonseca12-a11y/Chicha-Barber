from django import forms # type: ignore
from django.forms import ModelForm # type: ignore
from django.contrib.admin.widgets import FilteredSelectMultiple # type: ignore
from .models import Servicios,Promocion


class ServiciosForm(ModelForm):
    class Meta:
        model = Servicios
        fields=['nombre', 'precio', 'duracion', ]
        
class ServiciosEditarForm(ModelForm):
    class Meta:
        model = Servicios
        fields = '__all__'
        
class PromocionForm(ModelForm):
    class Meta:
        model = Promocion
        fields=['nombre', 'descuento', 'duracion', 'descripcion',]
        
class PromocionEditarForm(ModelForm):
    class Meta:
        model = Promocion
        fields = '__all__'
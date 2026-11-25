from django import forms
from django.core.exceptions import ValidationError
from .models import Reserva


class ValidacionTelefonoReservaMixin:
    def clean_telefono_usuario(self):
        telefono = self.cleaned_data.get('telefono_usuario')
        if not telefono:
            return telefono
        telefono = str(telefono).strip()
        if not telefono.isdigit():
            raise ValidationError('El teléfono solo puede contener números, sin espacios ni símbolos.')
        if len(telefono) < 7 or len(telefono) > 15:
            raise ValidationError('El teléfono debe tener entre 7 y 15 dígitos numéricos.')
        return telefono


# --- FORMULARIOS DE RESERVAS ---
class ReservaForm(ValidacionTelefonoReservaMixin, forms.ModelForm):
    fecha = forms.CharField(required=True)
    hora = forms.CharField(required=True)

    class Meta:
        model = Reserva
        fields = ['telefono_usuario', 'observacion']
        widgets = {
            'telefono_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '3001234567',
                'pattern': r'^\d{7,15}$',
                'title': 'Ingresa entre 7 y 15 dígitos numéricos.'
            }),
            'observacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas u observaciones adicionales'
            })
        }


class ReservaFormCompleto(ValidacionTelefonoReservaMixin, forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['telefono_usuario', 'observacion', 'fecha_reserva', 'servicio']


class ReservaEditarForm(ValidacionTelefonoReservaMixin, forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['telefono_usuario', 'observacion', 'fecha_reserva', 'estado']
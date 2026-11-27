from django import forms
from django.core.exceptions import ValidationError
from .models import Reserva, Agenda
from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone



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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            clase = (
                'form-select custom-white-input'
                if isinstance(campo.widget, forms.Select)
                else 'form-control custom-white-input'
            )
            campo.widget.attrs['class'] = (
                f"{campo.widget.attrs.get('class', '')} {clase}".strip()
            )
        
class ReprogramarReservaBarberoForm(forms.Form):
    """
    Reprogramación para el barbero: solo puede elegir otro turno
    disponible de su propia agenda. No edita ningún otro campo.
    """
    agenda = forms.ModelChoiceField(
        queryset=Agenda.objects.none(),
        label='Nuevo turno',
        empty_label='Selecciona un turno disponible',
        widget=forms.Select(attrs={'class': 'form-select custom-white-input'}),
    )

    def __init__(self, *args, reserva, **kwargs):
        super().__init__(*args, **kwargs)
        self.reserva = reserva

        hoy = timezone.localdate()
        ahora = timezone.localtime().time()

        turnos = Agenda.objects.filter(
            estado='disponible',
            profesional=reserva.agenda.profesional,
        ).filter(
            Q(fecha__gt=hoy) | Q(fecha=hoy, hora_inicio__gt=ahora)
        ).order_by('fecha', 'hora_inicio')

        campo = self.fields['agenda']
        campo.queryset = turnos
        campo.label_from_instance = lambda a: (
            f"{a.fecha:%d/%m/%Y}  {a.hora_inicio:%H:%M} - {a.hora_fin:%H:%M}"
        )

    def save(self):
        with transaction.atomic():
            nueva = Agenda.objects.select_for_update().get(
                pk=self.cleaned_data['agenda'].pk
            )
            if nueva.estado != 'disponible':
                raise ValidationError('Ese turno ya no está disponible.')

            anterior = self.reserva.agenda

            fecha_hora = datetime.combine(nueva.fecha, nueva.hora_inicio)
            if timezone.is_naive(fecha_hora):
                fecha_hora = timezone.make_aware(fecha_hora)

            self.reserva.agenda = nueva
            self.reserva.fecha_reserva = fecha_hora
            self.reserva.save()

            nueva.estado = 'reservada'
            nueva.save(update_fields=['estado'])

            if anterior and anterior.pk != nueva.pk:
                anterior.estado = 'disponible'
                anterior.save(update_fields=['estado'])

        return self.reserva
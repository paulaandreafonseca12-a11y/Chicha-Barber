from django import forms
from .models import Factura, DetalleFactura

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = [
            'cliente', 'metodo_pago', 'estado', 'total_pagado', 
            'nombre_cliente', 'correo_cliente', 'telefono_cliente'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'total_pagado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'nombre_cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre (opcional)'}),
            'correo_cliente': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo (opcional)'}),
            'telefono_cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono (opcional)'}),
        }

class DetalleFacturaForm(forms.ModelForm):
    class Meta:
        model = DetalleFactura
        fields = [
            'producto', 'reserva', 'cantidad', 'precio_unitario', 'subtotal'
        ]
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'reserva': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

# Formset para manejar múltiples detalles en una sola factura (POS del administrador)
DetalleFacturaFormSet = forms.inlineformset_factory(
    Factura, 
    DetalleFactura, 
    form=DetalleFacturaForm, 
    extra=1, 
    can_delete=True
)
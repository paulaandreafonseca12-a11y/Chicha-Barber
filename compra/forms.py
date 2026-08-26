from django import forms
from .models import Compra, DetalleCompra


class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['codigo_proveedor', 'observaciones']
        widgets = {
            'codigo_proveedor': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones'}),
        }
        labels = {
            'codigo_proveedor': 'Proveedor',
            'observaciones': 'Observaciones',
        }


class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['codigo_producto', 'cantidad', 'precio_compra', 'precio_venta']
        widgets = {
            'codigo_producto': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'required': True}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'required': True}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }
        labels = {
            'codigo_producto': 'Producto',
            'cantidad': 'Cantidad',
            'precio_compra': 'Precio de Compra',
            'precio_venta': 'Precio de Venta Sugerido',
        }

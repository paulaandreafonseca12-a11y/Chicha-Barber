from django import forms
from .models import Venta, DetalleVenta, DatosTransferencia


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = [
            'nombre_cliente',
            'correo',
            'telefono',
            'direccion',
            'metodo_pago',
            'estado_pago',
        ]
        widgets = {
            'nombre_cliente': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nombre completo', 'required': True}
            ),
            'correo': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}
            ),
            'telefono': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '3001234567'}
            ),
            'direccion': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Dirección de entrega'}
            ),
            'metodo_pago': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'estado_pago': forms.Select(
                attrs={'class': 'form-select'}
            ),
        }
        labels = {
            'nombre_cliente': 'Nombre del Cliente',
            'correo': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'metodo_pago': 'Método de Pago',
            'estado_pago': 'Estado del Pago',
        }


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = [
            'codigo_producto',
            'cantidad',
            'valor_descuento',
        ]
        widgets = {
            'codigo_producto': forms.Select(
                attrs={'class': 'form-select', 'required': True}
            ),
            'cantidad': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '1', 'value': '1', 'required': True}
            ),
            'valor_descuento': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'value': '0'}
            ),
        }
        labels = {
            'codigo_producto': 'Producto',
            'cantidad': 'Cantidad',
            'valor_descuento': 'Descuento',
        }


class DatosTransferenciaForm(forms.ModelForm):
    class Meta:
        model = DatosTransferencia
        fields = [
            'banco',
            'tipo_cuenta',
            'numero_cuenta',
            'titular',
            'instrucciones',
        ]
        widgets = {
            'banco': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nombre del banco', 'required': True}
            ),
            'tipo_cuenta': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ahorros / Corriente'}
            ),
            'numero_cuenta': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Número de cuenta'}
            ),
            'titular': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nombre del titular'}
            ),
            'instrucciones': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Instrucciones para transferir'}
            ),
        }

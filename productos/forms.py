from django import forms
from .models import Producto, Stock, Compra, DetalleCompra


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['nombre', 'descripcion']


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio_venta', 'precio_compra', 'stock']



class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['fecha_compra'] # Añade aquí los otros campos que necesites
        widgets = {
            'fecha_compra': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
# 🔥 FORMULARIO DE PAGO
class PagoForm(forms.Form):
    nombre = forms.CharField()
    correo = forms.EmailField()
    telefono = forms.CharField()
    direccion = forms.CharField()

    metodo_pago = forms.ChoiceField(
        choices=[
            ('persona', 'Pago en persona'),
            ('contraentrega', 'Pago contraentrega')
        ]
    )
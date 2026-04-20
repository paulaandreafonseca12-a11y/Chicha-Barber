from django import forms
from .models import Producto, Stock, Compra, DetalleCompra


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['nombre', 'descripcion']



class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio_venta', 'precio_compra', 'imagen', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'stock': forms.Select(attrs={'class': 'form-select'}),
        }
       

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['nombre_cliente', 'correo', 'telefono', 'direccion', 'metodo_pago']  # ← sin 'total'
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(
                choices=[
                    ('persona', 'Pago en persona'),
                    ('contraentrega', 'Pago contraentrega')
                ],
                attrs={'class': 'form-select'}
            ),
        }


class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


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
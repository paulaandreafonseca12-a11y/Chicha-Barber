from django import forms
from .models import Producto, Stock, Compra, DetalleCompra


# 🔹 FORMULARIO SOLO PRODUCTO (SIN STOCK)
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio_venta', 'precio_compra', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# 🔹 FORMULARIO SOLO PARA EDITAR STOCK
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['cantidad']
        widgets = {
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }


# 🔹 FORMULARIO DE COMPRA (Actualizado con Transferencia)
class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['nombre_cliente', 'correo', 'telefono', 'direccion', 'metodo_pago']
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(
                choices=[
                    ('persona', 'Pago en persona'),
                    ('contraentrega', 'Pago contraentrega'),
                    ('transferencia', 'Transferencia Bancaria')  # 🏦 Agregado
                ],
                attrs={'class': 'form-select'}
            ),
        }


# 🔹 FORMULARIO DETALLE DE COMPRA (VALIDA STOCK)
class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')

        if producto and cantidad:
            stock = getattr(producto, 'stock', None)

            if not stock:
                raise forms.ValidationError("Este producto no tiene stock registrado")

            if cantidad > stock.cantidad:
                raise forms.ValidationError(
                    f"Stock insuficiente. Disponible: {stock.cantidad}"
                )

        return cleaned_data


# 🔹 FORMULARIO DE PAGO (Actualizado con Transferencia)
class PagoForm(forms.Form):
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    direccion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    metodo_pago = forms.ChoiceField(
        choices=[
            ('persona', 'Pago en persona'),
            ('contraentrega', 'Pago contraentrega'),
            ('transferencia', 'Transferencia Bancaria')  # 🏦 Agregado
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
from django import forms
from .models import Producto, Stock, Compra, DetalleCompra


# 🔹 FORMULARIO PRODUCTO (MODO OSCURO + ESTADO CUADRADO)
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        # 🔑 Agregado 'estado' a la lista de campos visibles
        fields = ['nombre', 'descripcion', 'precio_venta', 'precio_compra', 'imagen', 'estado']
        widgets = { # Eliminado bg-dark y text-white para adaptación al tema
            'nombre': forms.TextInput(attrs={'class': 'form-control border-secondary'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control border-secondary', 'rows': 3}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control border-secondary'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control border-secondary'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control border-secondary'}),
            
            # 🔲 Cuadrado sencillo, tamaño estándar y con cursor de mano
            'estado': forms.CheckboxInput(attrs={
                'class': 'form-check-input', 
                'style': 'cursor: pointer; margin-left: 0;'
            }),
        }


# 🔹 FORMULARIO SOLO PARA EDITAR STOCK
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['cantidad']
        widgets = { # Eliminado bg-dark y text-white para adaptación al tema
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control border-secondary',
                'min': '0'
            }),
        }


# 🔹 FORMULARIO DE COMPRA (Actualizado con Transferencia)
class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['nombre_cliente', 'correo', 'telefono', 'direccion', 'metodo_pago']
        widgets = { # Eliminado bg-dark y text-white para adaptación al tema
            'nombre_cliente': forms.TextInput(attrs={'class': 'form-control border-secondary'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control border-secondary'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control border-secondary'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control border-secondary'}),
            'metodo_pago': forms.Select(
                choices=[
                    ('persona', 'Pago en persona'),
                    ('contraentrega', 'Pago contraentrega'),
                    ('transferencia', 'Transferencia Bancaria')
                ],
                attrs={'class': 'form-select border-secondary'}
            ),
        }


# 🔹 FORMULARIO DETALLE DE COMPRA (VALIDA STOCK)
class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad']
        widgets = { # Eliminado bg-dark y text-white para adaptación al tema
            'producto': forms.Select(attrs={'class': 'form-select border-secondary'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control border-secondary',
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
        widget=forms.TextInput(attrs={'class': 'form-control border-secondary'})
    )
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control border-secondary'})
    )
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control border-secondary'})
    )
    direccion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control border-secondary'})
    )
    metodo_pago = forms.ChoiceField(
        choices=[
            ('persona', 'Pago en persona'),
            ('contraentrega', 'Pago contraentrega'),
            ('transferencia', 'Transferencia Bancaria')
        ],
        widget=forms.Select(attrs={'class': 'form-select border-secondary'})
    )
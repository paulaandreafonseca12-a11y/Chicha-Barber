from django import forms
from .models import Producto, Stock, Compra, DetalleCompra, Proveedor, Categoria


# ==========================================
# 🔹 FORMULARIO PRODUCTO
# Solo información del catálogo
# ==========================================
class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto

        fields = [
            'nombre',
            'descripcion',
            'categoria',
            'imagen',
            'estado'
        ]

        widgets = {

            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            ),

            'categoria': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'imagen': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'estado': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),
        }



# ==========================================
# 🔹 FORMULARIO STOCK
# Cantidad, precios y proveedor
# ==========================================
class StockForm(forms.ModelForm):

    class Meta:

        model = Stock

        fields = [
            'cantidad',
            'precio_compra',
            'precio_venta',
            'proveedor'
        ]

        widgets = {

            'cantidad': forms.NumberInput(
                attrs={
                    'class':'form-control',
                    'min':'0'
                }
            ),

            'precio_compra': forms.NumberInput(
                attrs={
                    'class':'form-control'
                }
            ),

            'precio_venta': forms.NumberInput(
                attrs={
                    'class':'form-control'
                }
            ),

            'proveedor': forms.Select(
                attrs={
                    'class':'form-select'
                }
            ),

        }



# ==========================================
# 🔹 FORMULARIO COMPRA
# ==========================================
class CompraForm(forms.ModelForm):

    class Meta:

        model = Compra

        fields = [
            'nombre_cliente',
            'correo',
            'telefono',
            'direccion',
            'metodo_pago'
        ]

        widgets = {

            'nombre_cliente': forms.TextInput(
                attrs={
                    'class':'form-control'
                }
            ),

            'correo': forms.EmailInput(
                attrs={
                    'class':'form-control'
                }
            ),

            'telefono': forms.TextInput(
                attrs={
                    'class':'form-control'
                }
            ),

            'direccion': forms.TextInput(
                attrs={
                    'class':'form-control'
                }
            ),

            'metodo_pago': forms.Select(
                attrs={
                    'class':'form-select'
                }
            ),
        }



# ==========================================
# 🔹 FORMULARIO DETALLE COMPRA
# Validación de inventario
# ==========================================
class DetalleCompraForm(forms.ModelForm):

    class Meta:

        model = DetalleCompra

        fields = [
            'producto',
            'cantidad'
        ]

        widgets = {

            'producto': forms.Select(
                attrs={
                    'class':'form-select'
                }
            ),

            'cantidad': forms.NumberInput(
                attrs={
                    'class':'form-control',
                    'min':'1'
                }
            ),

        }


    def clean(self):

        cleaned_data = super().clean()

        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')


        if producto and cantidad:

            stock = getattr(producto, 'stock', None)


            if not stock:

                raise forms.ValidationError(
                    "Este producto no tiene stock registrado."
                )


            if cantidad > stock.cantidad:

                raise forms.ValidationError(
                    f"Stock insuficiente para {producto.nombre}. "
                    f"Disponible: {stock.cantidad}"
                )


        return cleaned_data




# ==========================================
# 🔹 FORMULARIO PAGO CLIENTE
# ==========================================
class PagoForm(forms.Form):

    nombre = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    )


    correo = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class':'form-control'
            }
        )
    )


    telefono = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    )


    direccion = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    )


    metodo_pago = forms.ChoiceField(

        choices=[
            ('persona','Pago en persona'),
            ('contraentrega','Pago contraentrega'),
            ('transferencia','Transferencia Bancaria')
        ],

        widget=forms.Select(
            attrs={
                'class':'form-select'
            }
        )
    )

class CategoriaForm(forms.ModelForm):
    
    class Meta:

        model = Categoria

        fields = [
            'nombre',
            'descripcion'
        ]

        widgets = {

            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control border-secondary',
                    'placeholder': 'Ingrese el nombre de la categoría'
                }
            ),


            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control border-secondary',
                    'placeholder': 'Descripción de la categoría',
                    'rows': 4
                }
            ),

        }


        labels = {

            'nombre': 'Nombre de Categoría',

            'descripcion': 'Descripción'

        }

# ==========================================
# 🔹 FORMULARIO PROVEEDOR
# ==========================================

class ProveedorForm(forms.ModelForm):

    class Meta:

        model = Proveedor

        fields = [
            'nombre',
            'telefono',
            'correo',
            'direccion'
        ]

        widgets = {

            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'correo': forms.EmailInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'direccion': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

        }
from django import forms

from .models import Compra, DetalleCompra


# ==========================================================
# FORMULARIO COMPRA
# ==========================================================

class CompraForm(forms.ModelForm):

    class Meta:
        model = Compra

        fields = [
            'codigo_proveedor',
            'observaciones',
        ]

        widgets = {
            'codigo_proveedor': forms.Select(
                attrs={
                    'class': 'form-select',
                    'required': True,
                }
            ),

            'observaciones': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Observaciones',
                }
            ),
        }

        labels = {
            'codigo_proveedor': 'Proveedor',
            'observaciones': 'Observaciones',
        }


# ==========================================================
# FORMULARIO DETALLE COMPRA
# ==========================================================

class DetalleCompraForm(forms.ModelForm):

    class Meta:
        model = DetalleCompra

        fields = [
            'codigo_producto',
            'cantidad',
            'precio_compra',
            'precio_venta',
        ]

        widgets = {
            'codigo_producto': forms.Select(
                attrs={
                    'class': 'form-select',
                    'required': True,
                }
            ),

            'cantidad': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'step': '1',
                    'required': True,
                }
            ),

            'precio_compra': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'max': '100000000',
                    'step': '0.01',
                    'required': True,
                }
            ),

            'precio_venta': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'max': '100000000',
                    'step': '0.01',
                }
            ),
        }

        labels = {
            'codigo_producto': 'Producto',
            'cantidad': 'Cantidad',
            'precio_compra': 'Precio de Compra',
            'precio_venta': 'Precio de Venta Sugerido',
        }

    # ======================================================
    # VALIDAR CANTIDAD
    # ======================================================

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')

        if cantidad is None or cantidad < 1:
            raise forms.ValidationError(
                'La cantidad debe ser mayor o igual a 1.'
            )

        if cantidad != int(cantidad):
            raise forms.ValidationError(
                'La cantidad debe ser un número entero.'
            )

        return cantidad

    # ======================================================
    # VALIDAR PRECIO DE COMPRA
    # ======================================================

    def clean_precio_compra(self):
        precio = self.cleaned_data.get('precio_compra')

        if precio is None:
            raise forms.ValidationError(
                'El precio de compra es obligatorio.'
            )

        if precio < 0:
            raise forms.ValidationError(
                'El precio de compra no puede ser negativo.'
            )

        if precio > 100000000:
            raise forms.ValidationError(
                'El precio de compra excede el valor máximo permitido.'
            )

        return precio

    # ======================================================
    # VALIDAR PRECIO DE VENTA
    # ======================================================

    def clean_precio_venta(self):
        precio = self.cleaned_data.get('precio_venta')

        if precio is not None:
            if precio < 0:
                raise forms.ValidationError(
                    'El precio de venta no puede ser negativo.'
                )

            if precio > 100000000:
                raise forms.ValidationError(
                    'El precio de venta excede el valor máximo permitido.'
                )

        return precio

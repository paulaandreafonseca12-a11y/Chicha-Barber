import re

from django import forms

from .models import (
    Venta,
    DetalleVenta,
    DetallePagos,
)


# ==========================================================
# VALIDACIÓN GENERAL: SOLO LETRAS Y ESPACIOS
# ==========================================================

def validar_solo_letras(valor, campo):
    """
    Permite letras, tildes, ñ, ü y espacios.
    No permite números ni símbolos.
    """

    if not valor or not valor.strip():
        raise forms.ValidationError(
            f'El campo {campo} es obligatorio.'
        )

    valor = valor.strip()

    if len(valor) < 2:
        raise forms.ValidationError(
            f'El campo {campo} debe tener al menos 2 caracteres.'
        )

    if not re.fullmatch(
        r'[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+',
        valor
    ):
        raise forms.ValidationError(
            f'El campo {campo} solo puede contener letras y espacios.'
        )

    return valor


# ==========================================================
# 1. FORMULARIO VENTA
# ==========================================================

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
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre completo',
                    'required': True,
                    'pattern': r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$',
                    'title': 'Ingrese únicamente letras y espacios.',
                }
            ),

            'correo': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'correo@ejemplo.com',
                }
            ),

            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '3001234567',
                    'pattern': r'^[0-9]+$',
                    'inputmode': 'numeric',
                    'minlength': '7',
                    'maxlength': '15',
                    'title': 'Ingrese entre 7 y 15 números.',
                }
            ),

            'direccion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Dirección de entrega',
                }
            ),

            'metodo_pago': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'estado_pago': forms.Select(
                attrs={
                    'class': 'form-select',
                }
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

    # VALIDAR NOMBRE DEL CLIENTE

    def clean_nombre_cliente(self):
        nombre = self.cleaned_data.get('nombre_cliente')

        return validar_solo_letras(
            nombre,
            'nombre del cliente'
        )

    # VALIDAR TELÉFONO

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not telefono:
            return telefono

        telefono = telefono.strip()

        if not telefono.isdigit():
            raise forms.ValidationError(
                'El teléfono solo puede contener números.'
            )

        if len(telefono) < 7 or len(telefono) > 15:
            raise forms.ValidationError(
                'El teléfono debe tener entre 7 y 15 números.'
            )

        return telefono

    # VALIDAR DIRECCIÓN

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')

        if not direccion:
            return direccion

        direccion = direccion.strip()

        if not re.fullmatch(
            r'[a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ\s.,#°/\-]+',
            direccion
        ):
            raise forms.ValidationError(
                'La dirección contiene caracteres no permitidos.'
            )

        return direccion


# ==========================================================
# 2. FORMULARIO DETALLE DE VENTA
# ==========================================================

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

            'valor_descuento': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'step': '0.01',
                }
            ),
        }

        labels = {
            'codigo_producto': 'Producto',
            'cantidad': 'Cantidad',
            'valor_descuento': 'Descuento',
        }

    # VALIDAR CANTIDAD

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')

        if cantidad is None:
            raise forms.ValidationError(
                'La cantidad es obligatoria.'
            )

        if cantidad < 1:
            raise forms.ValidationError(
                'La cantidad debe ser mayor o igual a 1.'
            )

        if cantidad != int(cantidad):
            raise forms.ValidationError(
                'La cantidad debe ser un número entero.'
            )

        return cantidad

    # VALIDAR DESCUENTO

    def clean_valor_descuento(self):
        descuento = self.cleaned_data.get('valor_descuento')

        if descuento is None:
            return 0

        if descuento < 0:
            raise forms.ValidationError(
                'El descuento no puede ser negativo.'
            )

        return descuento

    # VALIDAR STOCK DISPONIBLE

    def clean(self):
        cleaned_data = super().clean()

        producto = cleaned_data.get('codigo_producto')
        cantidad = cleaned_data.get('cantidad')

        if producto is not None and cantidad is not None:
            try:
                stock = producto.detalle_producto.cantidad_actual

            except AttributeError:
                raise forms.ValidationError(
                    f'El producto "{producto.nombre}" '
                    'no tiene un registro de stock.'
                )

            if cantidad > stock:
                raise forms.ValidationError(
                    f'Stock insuficiente para "{producto.nombre}". '
                    f'Disponible: {stock}.'
                )

        return cleaned_data


# ==========================================================
# 3. FORMULARIO DATOS DE TRANSFERENCIA
# ==========================================================

class DetallePagosForm(forms.ModelForm):

    class Meta:
        model = DetallePagos

        fields = [
            'banco',
            'tipo_cuenta',
            'numero_cuenta',
            'titular',
            'instrucciones',
        ]

        widgets = {
            'banco': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre del banco',
                    'required': True,
                }
            ),

            'tipo_cuenta': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ahorros / Corriente',
                }
            ),

            'numero_cuenta': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Número de cuenta',
                    'inputmode': 'numeric',
                    'pattern': r'^[0-9]+$',
                    'title': 'El número de cuenta solo puede contener números.',
                }
            ),

            'titular': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre del titular',
                    'pattern': r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$',
                    'title': 'Ingrese únicamente letras y espacios.',
                }
            ),

            'instrucciones': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': (
                        'Instrucciones para realizar la transferencia'
                    ),
                }
            ),
        }

        labels = {
            'banco': 'Banco',
            'tipo_cuenta': 'Tipo de Cuenta',
            'numero_cuenta': 'Número de Cuenta',
            'titular': 'Titular',
            'instrucciones': 'Instrucciones',
        }

    # VALIDAR BANCO

    def clean_banco(self):
        banco = self.cleaned_data.get('banco')

        if not banco or not banco.strip():
            raise forms.ValidationError(
                'El banco es obligatorio.'
            )

        banco = banco.strip()

        if len(banco) < 2:
            raise forms.ValidationError(
                'El nombre del banco debe tener al menos 2 caracteres.'
            )

        return banco

    # VALIDAR TIPO DE CUENTA

    def clean_tipo_cuenta(self):
        tipo = self.cleaned_data.get('tipo_cuenta')

        if not tipo:
            return tipo

        return tipo.strip()

    # VALIDAR NÚMERO DE CUENTA

    def clean_numero_cuenta(self):
        numero = self.cleaned_data.get('numero_cuenta')

        if not numero:
            return numero

        numero = numero.strip()

        if not numero.isdigit():
            raise forms.ValidationError(
                'El número de cuenta solo puede contener números.'
            )

        return numero

    # VALIDAR TITULAR

    def clean_titular(self):
        titular = self.cleaned_data.get('titular')

        if not titular:
            return titular

        return validar_solo_letras(
            titular,
            'nombre del titular'
        )

    # VALIDAR INSTRUCCIONES

    def clean_instrucciones(self):
        instrucciones = self.cleaned_data.get('instrucciones')

        if not instrucciones:
            return instrucciones

        return instrucciones.strip()

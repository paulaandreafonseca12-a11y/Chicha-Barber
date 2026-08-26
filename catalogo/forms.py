import re
from django import forms
from .models import Producto, Categoria, Proveedor, Marca, DetalleProducto


# ==========================================================
# VALIDACIONES GENERALES
# ==========================================================

def validar_texto(valor, campo):
    if not valor:
        raise forms.ValidationError(f'El campo {campo} es obligatorio.')
    valor = valor.strip()
    if not re.fullmatch(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+', valor):
        raise forms.ValidationError(
            f'El campo {campo} solo puede contener letras, números y espacios.'
        )
    return valor


def validar_descripcion(valor, campo):
    if not valor:
        return valor
    valor = valor.strip()
    if not re.fullmatch(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,#\-_/()]+', valor):
        raise forms.ValidationError(
            f'El campo {campo} contiene caracteres no permitidos.'
        )
    return valor


# ==========================================================
# FORMULARIO PRODUCTO
# ==========================================================

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'descripcion',
            'codigo_categoria',
            'codigo_marca',
            'precio',
            'imagen',
            'estado',
        ]
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre del producto',
                    'pattern': r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$',
                    'title': 'El nombre solo puede contener letras, números y espacios.',
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Descripción del producto',
                }
            ),
            'codigo_categoria': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'codigo_marca': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'precio': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'step': '0.01',
                    'placeholder': 'Precio',
                }
            ),
            'imagen': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'estado': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'codigo_categoria': 'Categoría',
            'codigo_marca': 'Marca',
            'precio': 'Precio',
            'imagen': 'Imagen',
            'estado': 'Activo',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        return validar_texto(nombre, 'nombre del producto')

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        return validar_descripcion(descripcion, 'descripción')

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        return precio


# ==========================================================
# FORMULARIO DETALLE PRODUCTO (STOCK / EXISTENCIAS)
# ==========================================================

class DetalleProductoForm(forms.ModelForm):
    class Meta:
        model = DetalleProducto
        fields = [
            'cantidad_actual',
            'stock_min',
            'stock_max',
            'observaciones'
        ]
        widgets = {
            'cantidad_actual': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'step': '1',
                }
            ),
            'stock_min': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'step': '1',
                }
            ),
            'stock_max': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'step': '1',
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

    def clean_cantidad_actual(self):
        cantidad = self.cleaned_data.get('cantidad_actual')
        if cantidad is not None and cantidad < 0:
            raise forms.ValidationError('La cantidad actual no puede ser negativa.')
        return cantidad

    def clean_stock_min(self):
        stock_min = self.cleaned_data.get('stock_min')
        if stock_min is not None and stock_min < 0:
            raise forms.ValidationError('El stock mínimo no puede ser negativo.')
        return stock_min

    def clean_stock_max(self):
        stock_max = self.cleaned_data.get('stock_max')
        if stock_max is not None and stock_max < 0:
            raise forms.ValidationError('El stock máximo no puede ser negativo.')
        return stock_max

    def clean(self):
        cleaned_data = super().clean()
        stock_min = cleaned_data.get('stock_min')
        stock_max = cleaned_data.get('stock_max')
        if stock_min is not None and stock_max is not None and stock_max < stock_min:
            raise forms.ValidationError('El stock máximo no puede ser menor que el stock mínimo.')
        return cleaned_data


# ==========================================================
# FORMULARIO CATEGORÍA
# ==========================================================

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
                    'placeholder': 'Ingrese el nombre de la categoría',
                    'pattern': r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$',
                    'title': 'Solo se permiten letras, números y espacios.',
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control border-secondary',
                    'placeholder': 'Descripción de la categoría',
                    'rows': 4,
                }
            ),
        }
        labels = {
            'nombre': 'Nombre de Categoría',
            'descripcion': 'Descripción'
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        return validar_texto(nombre, 'nombre de la categoría')

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        return validar_descripcion(descripcion, 'descripción')


# ==========================================================
# FORMULARIO PROVEEDOR
# ==========================================================

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
                    'class': 'form-control',
                    'placeholder': 'Nombre del proveedor',
                    'pattern': r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$',
                    'title': 'Solo se permiten letras, números y espacios.',
                }
            ),
            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '3001234567',
                    'pattern': r'^[0-9]+$',
                    'inputmode': 'numeric',
                    'title': 'El teléfono solo puede contener números.',
                }
            ),
            'correo': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'correo@ejemplo.com',
                }
            ),
            'direccion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Calle 10 # 20-30',
                }
            ),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        return validar_texto(nombre, 'nombre del proveedor')

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono:
            return telefono
        telefono = telefono.strip()
        if not telefono.isdigit():
            raise forms.ValidationError('El teléfono solo puede contener números.')
        if len(telefono) < 7 or len(telefono) > 15:
            raise forms.ValidationError('El teléfono debe tener entre 7 y 15 números.')
        return telefono


# ==========================================================
# FORMULARIO MARCA
# ==========================================================

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = [
            'nombre',
            'descripcion',
            'estado',
        ]
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre de la marca',
                    'pattern': r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$',
                    'title': 'El nombre solo puede contener letras, números y espacios.',
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Descripción de la marca',
                    'rows': 3,
                }
            ),
            'estado': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }
        labels = {
            'nombre': 'Nombre de la Marca',
            'descripcion': 'Descripción',
            'estado': 'Activo',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise forms.ValidationError('El nombre de la marca es obligatorio.')
        nombre = nombre.strip()
        if len(nombre) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        if not re.fullmatch(r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+', nombre):
            raise forms.ValidationError('El nombre solo puede contener letras, números y espacios.')
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        return validar_descripcion(descripcion, 'descripción')

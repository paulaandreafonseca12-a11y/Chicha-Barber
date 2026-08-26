from django import forms # type: ignore
from django.forms import ModelForm # type: ignore
from django.contrib.admin.widgets import FilteredSelectMultiple # type: ignore
from .models import  Promocion

class PromocionForm(ModelForm):
    class Meta:
        model = Promocion

        fields = [
            'codigo_servicio',
            'codigo_producto',
            'nombre',
            'porcentaje_descuento',
            'fecha_inicio',
            'fecha_fin',
            'descripcion',
            'imagen',
            'estado',
        ]

        widgets = {

            'codigo_servicio': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'codigo_producto': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. Promoción de Verano',
                    'pattern': r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$',
                    'title': 'El nombre solo puede contener letras, números y espacios.',
                }
            ),

            'porcentaje_descuento': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'max': '50',
                    'step': '0.01',
                    'placeholder': 'Ej. 20',
                    'title': 'El descuento debe estar entre 0 y 50.',
                }
            ),

            'fecha_inicio': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'fecha_fin': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Descripción de la promoción',
                    'rows': 3,
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
            'codigo_servicio': 'Servicio Asociado',
            'codigo_producto': 'Producto Asociado',
            'nombre': 'Nombre de la Promoción',
            'porcentaje_descuento': 'Porcentaje de Descuento',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'descripcion': 'Descripción',
            'imagen': 'Imagen',
            'estado': 'Activo',
        }

    # ------------------------------------------------------
    # VALIDAR NOMBRE
    # ------------------------------------------------------

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not nombre:
            raise forms.ValidationError(
                'El nombre de la promoción es obligatorio.'
            )

        nombre = nombre.strip()

        if len(nombre) < 2:
            raise forms.ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )

        if not re.fullmatch(
            r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+',
            nombre
        ):
            raise forms.ValidationError(
                'El nombre solo puede contener letras, números y espacios.'
            )

        return nombre

    # ------------------------------------------------------
    # VALIDAR PORCENTAJE
    # ------------------------------------------------------

    def clean_porcentaje_descuento(self):
        porcentaje = self.cleaned_data.get(
            'porcentaje_descuento'
        )

        if porcentaje is None:
            raise forms.ValidationError(
                'El porcentaje de descuento es obligatorio.'
            )

        if porcentaje < 0 or porcentaje > 50:
            raise forms.ValidationError(
                'El porcentaje de descuento debe estar entre 0 y 50.'
            )

        return porcentaje

    # ------------------------------------------------------
    # VALIDAR DESCRIPCIÓN
    # ------------------------------------------------------

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')

        if not descripcion:
            return descripcion

        descripcion = descripcion.strip()

        if len(descripcion) < 10:
            raise forms.ValidationError(
                'La descripción debe tener al menos 10 caracteres.'
            )

        if not re.fullmatch(
            r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,#*/()_-]+',
            descripcion
        ):
            raise forms.ValidationError(
                'La descripción contiene caracteres no permitidos.'
            )

        return descripcion

    # ------------------------------------------------------
    # VALIDAR FECHAS Y ASOCIACIÓN
    # ------------------------------------------------------

    def clean(self):
        cleaned_data = super().clean()

        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin:

            if fecha_fin < fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de finalización no puede ser anterior '
                    'a la fecha de inicio.'
                )

        codigo_producto = cleaned_data.get(
            'codigo_producto'
        )

        codigo_servicio = cleaned_data.get(
            'codigo_servicio'
        )

        if not codigo_producto and not codigo_servicio:
            raise forms.ValidationError(
                'La promoción debe estar asociada a un producto '
                'o a un servicio.'
            )

        return cleaned_data


# ==========================================================
# FORMULARIO EDITAR PROMOCIÓN
# ==========================================================

class PromocionEditarForm(forms.ModelForm):

    class Meta:
        model = Promocion

        fields = [
            'codigo_servicio',
            'codigo_producto',
            'nombre',
            'porcentaje_descuento',
            'fecha_inicio',
            'fecha_fin',
            'descripcion',
            'imagen',
            'estado',
        ]

        widgets = {

            'codigo_servicio': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'codigo_producto': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre de la promoción',
                }
            ),

            'porcentaje_descuento': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'max': '50',
                    'step': '0.01',
                }
            ),

            'fecha_inicio': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'fecha_fin': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Descripción de la promoción',
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
            'codigo_servicio': 'Servicio Asociado',
            'codigo_producto': 'Producto Asociado',
            'nombre': 'Nombre de la Promoción',
            'porcentaje_descuento': 'Porcentaje de Descuento',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin',
            'descripcion': 'Descripción',
            'imagen': 'Imagen',
            'estado': 'Activo',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not nombre:
            raise forms.ValidationError(
                'El nombre de la promoción es obligatorio.'
            )

        nombre = nombre.strip()

        if len(nombre) < 2:
            raise forms.ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )

        if not re.fullmatch(
            r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+',
            nombre
        ):
            raise forms.ValidationError(
                'El nombre solo puede contener letras, números y espacios.'
            )

        return nombre

    def clean_porcentaje_descuento(self):
        porcentaje = self.cleaned_data.get(
            'porcentaje_descuento'
        )

        if porcentaje is None:
            raise forms.ValidationError(
                'El porcentaje de descuento es obligatorio.'
            )

        if porcentaje < 0 or porcentaje > 50:
            raise forms.ValidationError(
                'El porcentaje de descuento debe estar entre 0 y 50.'
            )

        return porcentaje

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')

        if not descripcion:
            return descripcion

        descripcion = descripcion.strip()

        if len(descripcion) < 10:
            raise forms.ValidationError(
                'La descripción debe tener al menos 10 caracteres.'
            )

        if not re.fullmatch(
            r'[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,#*/()_-]+',
            descripcion
        ):
            raise forms.ValidationError(
                'La descripción contiene caracteres no permitidos.'
            )

        return descripcion

    def clean(self):
        cleaned_data = super().clean()

        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin:

            if fecha_fin < fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de finalización no puede ser anterior '
                    'a la fecha de inicio.'
                )

        codigo_producto = cleaned_data.get(
            'codigo_producto'
        )

        codigo_servicio = cleaned_data.get(
            'codigo_servicio'
        )

        if not codigo_producto and not codigo_servicio:
            raise forms.ValidationError(
                'La promoción debe estar asociada a un producto '
                'o a un servicio.'
            )

        return cleaned_data
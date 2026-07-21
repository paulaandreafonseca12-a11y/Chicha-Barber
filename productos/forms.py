from django import forms
from .models import Producto, Stock, Compra, DetalleCompra, Categoria, Proveedor

# ==========================================
# 🔹 FORMULARIO PRODUCTO (Con campos de Stock y Proveedor unificados)
# ==========================================
class ProductoForm(forms.ModelForm):
    # 🌟 Campos extra que pertenecen al modelo Stock, pero los manejamos aquí
    cantidad = forms.IntegerField(
        min_value=0, 
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control bg-white text-dark border-secondary'}),
        label="Cantidad en Stock"
    )
    precio_compra = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        initial=0.00,
        widget=forms.NumberInput(attrs={'class': 'form-control bg-white text-dark border-secondary'}),
        label="Precio de Compra"
    )
    precio_venta = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        initial=0.00,
        widget=forms.NumberInput(attrs={'class': 'form-control bg-white text-dark border-secondary'}),
        label="Precio de Venta"
    )
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.all(),
        required=False,
        empty_label="Seleccione un proveedor",
        widget=forms.Select(attrs={'class': 'form-select bg-white text-dark border-secondary'}),
        label="Proveedor"
    )

    class Meta:
        model = Producto
        # Agregamos 'categoria' y 'estado'
        fields = ['nombre', 'descripcion', 'categoria', 'imagen', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control bg-white text-dark border-secondary'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control bg-white text-dark border-secondary', 'rows': 3}),
            'categoria': forms.Select(attrs={'class': 'form-select bg-white text-dark border-secondary'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control bg-white text-dark border-secondary'}),
            'estado': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'cursor: pointer;'
            }),
        }

    def __init__(self, *args, **kwargs):
        """ Llena los campos de Stock si estamos editando un producto existente """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            stock = getattr(self.instance, 'stock', None)
            if stock:
                self.fields['cantidad'].initial = stock.cantidad
                self.fields['precio_compra'].initial = stock.precio_compra
                self.fields['precio_venta'].initial = stock.precio_venta
                self.fields['proveedor'].initial = stock.proveedor

    def save(self, commit=True):
        """ Guarda el producto y automáticamente actualiza o crea su registro de Stock """
        producto = super().save(commit=commit)
        
        # Obtenemos los valores limpios del formulario
        cantidad = self.cleaned_data.get('cantidad')
        precio_compra = self.cleaned_data.get('precio_compra')
        precio_venta = self.cleaned_data.get('precio_venta')
        proveedor = self.cleaned_data.get('proveedor')

        if commit:
            # Como tu signal crea un Stock por defecto en 0, lo buscamos o creamos
            stock, created = Stock.objects.get_or_create(producto=producto)
            stock.cantidad = cantidad
            stock.precio_compra = precio_compra
            stock.precio_venta = precio_venta
            stock.proveedor = proveedor
            stock.save()

        return producto


# ==========================================
# 🔹 FORMULARIO SOLO PARA EDITAR STOCK (Rápido)
# ==========================================
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['cantidad', 'precio_compra', 'precio_venta', 'proveedor']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control border-secondary', 'min': '0'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control border-secondary'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control border-secondary'}),
            'proveedor': forms.Select(attrs={'class': 'form-select border-secondary'}),
        }


# ==========================================
# 🔹 FORMULARIO DE COMPRA (Se mantiene igual)
# ==========================================
class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['nombre_cliente', 'correo', 'telefono', 'direccion', 'metodo_pago']
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={'class': 'form-control border-secondary'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control border-secondary'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control border-secondary'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control border-secondary'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select border-secondary'}),
        }


# ==========================================
# 🔹 FORMULARIO DETALLE DE COMPRA (Valida Stock desde la nueva ubicación)
# ==========================================
class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select border-secondary'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control border-secondary', 'min': '1'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')

        if producto and cantidad:
            stock = getattr(producto, 'stock', None)

            if not stock:
                raise forms.ValidationError("Este producto no tiene control de stock registrado.")

            if cantidad > stock.cantidad:
                raise forms.ValidationError(
                    f"Stock insuficiente para {producto.nombre}. Disponible: {stock.cantidad}"
                )

        return cleaned_data


# ==========================================
# 🔹 FORMULARIO DE PAGO (Se mantiene igual)
# ==========================================
class PagoForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-secondary'}))
    correo = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control border-secondary'}))
    telefono = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-secondary'}))
    direccion = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-secondary'}))
    metodo_pago = forms.ChoiceField(
        choices=[
            ('persona', 'Pago en persona'),
            ('contraentrega', 'Pago contraentrega'),
            ('transferencia', 'Transferencia Bancaria')
        ],
        widget=forms.Select(attrs={'class': 'form-select border-secondary'})
    )
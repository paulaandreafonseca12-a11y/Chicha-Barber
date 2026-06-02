from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# 🔹 PRODUCTO
class Producto(models.Model):
    codigo_producto = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.codigo:
            self.codigo = f"PROD-{self.codigo_producto:05d}"
            super().save(update_fields=['codigo'])

    @property
    def stock_actual(self):
        if hasattr(self, 'stock') and self.stock is not None:
            return self.stock.cantidad
        return 0

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# 🔹 STOCK
class Stock(models.Model):
    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name="stock",
        null=True,
        blank=True
    )
    cantidad = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.producto.nombre if self.producto else 'Sin producto'} - Stock: {self.cantidad}"


# 🔹 MOVIMIENTO INVENTARIO
class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='movimientos',
        verbose_name='Producto'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo de movimiento')
    cantidad = models.PositiveIntegerField(verbose_name='Cantidad')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')
    motivo = models.CharField(max_length=200, verbose_name='Motivo')

    def __str__(self):
        return f"{self.producto.codigo} - {self.tipo} {self.cantidad}"


# 🔥 SIGNAL → crear stock automático
@receiver(post_save, sender=Producto)
def crear_stock(sender, instance, created, **kwargs):
    if created:
        Stock.objects.get_or_create(producto=instance, defaults={'cantidad': 0})


# 🔹 COMPRA (Modificado para soportar estados de Transferencia)
class Compra(models.Model):
    METODO_PAGO_CHOICES = [
        ('persona', 'Pago en persona'),
        ('contraentrega', 'Pago contraentrega'),
        ('transferencia', 'Transferencia Bancaria'),
    ]

    ESTADO_PAGO_CHOICES = [
        ('pendiente_verificacion', 'Pendiente de Verificación'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    codigo_compra = models.AutoField(primary_key=True)
    nombre_cliente = models.CharField(max_length=100)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    
    # Vinculado a las opciones del formulario
    metodo_pago = models.CharField(max_length=50, choices=METODO_PAGO_CHOICES, blank=True, null=True)
    estado_pago = models.CharField(max_length=30, choices=ESTADO_PAGO_CHOICES, default='completado')
    
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta #{self.codigo_compra} - {self.nombre_cliente} ({self.get_metodo_pago_display()})"


# 🔹 DETALLE DE COMPRA
class DetalleCompra(models.Model):
    codigo_detalle = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.producto.precio_venta

        # Validar stock antes de guardar
        stock = self.producto.stock
        if self.cantidad > stock.cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {stock.cantidad}")

        super().save(*args, **kwargs)

        # Descontar stock
        stock.cantidad -= self.cantidad
        stock.save()

        # Registrar el movimiento de salida en el inventario de forma automática
        MovimientoInventario.objects.create(
            producto=self.producto,
            tipo='salida',
            cantidad=self.cantidad,
            motivo=f"Venta Online #{self.compra.codigo_compra}"
        )

        # Actualizar total de compra
        self.compra.total = sum(d.subtotal for d in self.compra.detalles.all())
        self.compra.save()

    def __str__(self):
        return f"{self.producto.codigo} x {self.cantidad}"

class DatosTransferencia(models.Model):
    banco = models.CharField(max_length=100)
    tipo_cuenta = models.CharField(max_length=100)
    numero_cuenta = models.CharField(max_length=100)
    titular = models.CharField(max_length=100)
    instrucciones = models.TextField(help_text="Nota o advertencia para el cliente")

    class Meta:
        verbose_name = "Datos de Transferencia"
        verbose_name_plural = "Datos de Transferencia"

    @classmethod
    def get_solo(cls):
        """Retorna la única instancia de configuración o crea una nueva."""
        obj, created = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return f"Configuración: {self.banco}"
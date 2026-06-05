from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from usuarios.models import Usuario

# ==========================================
# 🔹 PRODUCTO
# ==========================================
class Producto(models.Model):
    codigo_producto = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(default=True)  # True = Activo, False = Inactivo
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

    # 🔹 Métodos de clase optimizados para alimentar tus tarjetas de resumen
    @classmethod
    def total_productos(cls):
        return cls.objects.count()

    @classmethod
    def total_activos(cls):
        return cls.objects.filter(estado=True).count()

    @classmethod
    def total_inactivos(cls):
        return cls.objects.filter(estado=False).count()

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ==========================================
# 🔹 STOCK
# ==========================================
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


# ==========================================
# 🔹 MOVIMIENTO INVENTARIO
# ==========================================
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


# 🔥 SIGNAL → Crear stock automático al registrar un producto
@receiver(post_save, sender=Producto)
def crear_stock(sender, instance, created, **kwargs):
    if created:
        Stock.objects.get_or_create(producto=instance, defaults={'cantidad': 0})


# ==========================================
# 🔹 COMPRA / VENTA MADRE
# ==========================================
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
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compras',
        verbose_name='Usuario'
    )
    nombre_cliente = models.CharField(max_length=100)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    
    metodo_pago = models.CharField(max_length=50, choices=METODO_PAGO_CHOICES, blank=True, null=True)
    estado_pago = models.CharField(max_length=30, choices=ESTADO_PAGO_CHOICES, default='completado')
    
    comprobante = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def actualizar_total(self):
        """
        Recalcula el total de la compra sumando los subtotales de sus detalles.
        """
        self.total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.save(update_fields=['total'])

    def __str__(self):
        return f"Venta #{self.codigo_compra} - {self.nombre_cliente} ({self.get_metodo_pago_display()})"


# ==========================================
# 🔹 DETALLE DE COMPRA
# ==========================================
class DetalleCompra(models.Model):
    codigo_detalle = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # 1. Calcular de manera estricta el subtotal antes de guardar en la BD
        self.subtotal = self.cantidad * self.producto.precio_venta

        # 2. Validar disponibilidad real en el inventario
        stock = self.producto.stock
        if self.cantidad > stock.cantidad:
            raise ValueError(f"Stock insuficiente para '{self.producto.nombre}'. Disponible: {stock.cantidad}")

        # 3. Guardar el registro del detalle de compra
        super().save(*args, **kwargs)

        # 4. Descontar las unidades adquiridas del stock global
        stock.cantidad -= self.cantidad
        stock.save(update_fields=['cantidad'])

        # 5. Insertar automáticamente la bitácora de la salida en el histórico de inventario
        MovimientoInventario.objects.create(
            producto=self.producto,
            tipo='salida',
            cantidad=self.cantidad,
            motivo=f"Venta Online #{self.compra.codigo_compra}"
        )

    def __str__(self):
        return f"{self.producto.codigo} x {self.cantidad}"


# ==========================================
# 🔹 DATOS DE TRANSFERENCIA
# ==========================================
class DatosTransferencia(models.Model):
    banco = models.CharField(max_length=100, default="Banco por definir")
    tipo_cuenta = models.CharField(max_length=50, blank=True, null=True)
    numero_cuenta = models.CharField(max_length=50, blank=True, null=True)
    titular = models.CharField(max_length=100, blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Datos de Transferencia - {self.banco}"
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# 🔹 PRODUCTO
class Producto(models.Model):
    codigo_producto = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Guardar primero para obtener ID
        super().save(*args, **kwargs)

        # Generar código automático
        if not self.codigo:
            self.codigo = f"PROD-{self.codigo_producto:05d}"
            super().save(update_fields=['codigo'])

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# 🔹 STOCK
class Stock(models.Model):
    producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        related_name="stock"
    )
    cantidad = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.producto.nombre} - Stock: {self.cantidad}"


# 🔥 SIGNAL → crear stock automático
@receiver(post_save, sender=Producto)
def crear_stock(sender, instance, created, **kwargs):
    if created:
        Stock.objects.get_or_create(producto=instance, defaults={'cantidad': 0})


# 🔹 COMPRA
class Compra(models.Model):
    codigo_compra = models.AutoField(primary_key=True)
    nombre_cliente = models.CharField(max_length=100)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta #{self.codigo_compra} - {self.nombre_cliente}"


# 🔹 DETALLE DE COMPRA
class DetalleCompra(models.Model):
    codigo_detalle = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calcular subtotal
        self.subtotal = self.cantidad * self.producto.precio_venta

        # 🔥 Validar stock antes de guardar
        stock = self.producto.stock

        if self.cantidad > stock.cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {stock.cantidad}")

        # Guardar detalle
        super().save(*args, **kwargs)

        # 🔥 Descontar stock
        stock.cantidad -= self.cantidad
        stock.save()

        # 🔥 Actualizar total de compra
        self.compra.total = sum(d.subtotal for d in self.compra.detalles.all())
        self.compra.save()

    def __str__(self):
        return f"{self.producto.codigo} x {self.cantidad}"
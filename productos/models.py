from django.db import models

class Stock(models.Model):
    codigo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigo_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="productos"
    )

    def __str__(self):
        return self.nombre

class Compra(models.Model):  # En realidad es una Venta al cliente
    codigo_compra = models.AutoField(primary_key=True)
    # Datos del cliente
    nombre_cliente = models.CharField(max_length=100, verbose_name="Nombre del Cliente")
    correo = models.EmailField(verbose_name="Correo", blank=True, null=True)
    telefono = models.CharField(max_length=20, verbose_name="Teléfono", blank=True, null=True)
    direccion = models.CharField(max_length=200, verbose_name="Dirección", blank=True, null=True)
    metodo_pago = models.CharField(max_length=50, verbose_name="Método de Pago", blank=True, null=True)
    # Totales y fechas
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_compra = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Compra")

    def __str__(self):
        return f"Venta #{self.codigo_compra} - {self.nombre_cliente}"

class DetalleCompra(models.Model):
    codigo_detalle = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.producto.precio_venta  # ← precio_venta, no precio_compra
        super().save(*args, **kwargs)
        self.compra.total = sum(d.subtotal for d in self.compra.detalles.all())
        self.compra.save()

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
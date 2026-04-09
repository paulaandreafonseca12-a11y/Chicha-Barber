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

class Compra(models.Model):
    codigo_compra = models.AutoField(primary_key=True)
    proveedor = models.CharField(max_length=100, verbose_name="Proveedor") # Ajustado para CB-51
    # CB-58: Permitir registrar fecha de compra
    fecha_compra = models.DateField(verbose_name="Fecha de Compra")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compra #{self.codigo_compra} - {self.fecha_compra}"

class DetalleCompra(models.Model):
    codigo_detalle = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    cantidad = models.IntegerField()
    # CB-59: El sistema debe guardar el total (subtotal) automáticamente
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calcula el subtotal automáticamente usando el precio_compra del producto
        self.subtotal = self.cantidad * self.producto.precio_compra
        super().save(*args, **kwargs)
        
        # Al guardar un detalle, actualizamos el total de la compra padre
        self.compra.total = sum(d.subtotal for d in self.compra.detalles.all())
        self.compra.save()

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
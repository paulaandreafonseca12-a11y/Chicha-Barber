from django.db import models


class Stock(models.Model):
    codigo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    cantidad = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} - Stock: {self.cantidad}"


class Producto(models.Model):
    codigo_producto = models.AutoField(primary_key=True)

    # 🔥 Código visible tipo PROD-001
    codigo = models.CharField(max_length=20, unique=True, blank=True)

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="productos"
    )

    def save(self, *args, **kwargs):
        if not self.codigo:
            ultimo = Producto.objects.order_by('-codigo_producto').first()
            if ultimo:
                numero = ultimo.codigo_producto + 1
            else:
                numero = 1

            self.codigo = f"PROD-{numero:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Compra(models.Model):
    codigo_compra = models.AutoField(primary_key=True)
    nombre_cliente = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    metodo_pago = models.CharField(max_length=20)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_cliente} - Compra {self.codigo_compra}"


class DetalleCompra(models.Model):
    codigo_detalle = models.AutoField(primary_key=True)

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )

    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.codigo} x {self.cantidad}"


class Pago(models.Model):
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name="pagos"
    )

    METODOS_PAGO = [
        ('persona', 'Pago en persona'),
        ('contraentrega', 'Pago contraentrega'),
    ]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)

    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago de {self.nombre} - Compra {self.compra.codigo_compra}"
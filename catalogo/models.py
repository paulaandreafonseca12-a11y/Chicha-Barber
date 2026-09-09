from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from servicios.models import Servicios


# ==========================================================
# 1. CATEGORÍA
# ==========================================================

class Categoria(models.Model):

    codigo = models.AutoField(primary_key=True)

    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la Categoría",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"


# ==========================================================
# 2. PROVEEDOR
# ==========================================================

class Proveedor(models.Model):

    codigo = models.AutoField(primary_key=True)

    nombre = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nombre del Proveedor",
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono",
    )

    correo = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Correo Electrónico",
    )

    direccion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Dirección",
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"


# ==========================================================
# 3. MARCA
# ==========================================================

class Marca(models.Model):

    codigo = models.AutoField(primary_key=True)

    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la Marca",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
    )

    estado = models.BooleanField(
        default=True,
        verbose_name="Estado",
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"


# ==========================================================
# 4. PRODUCTO
# ==========================================================

class Producto(models.Model):

    codigo_producto = models.AutoField(
        primary_key=True
    )

    codigo = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    codigo_detalle_producto = models.ForeignKey(
        "DetalleProducto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="producto_principal",
        verbose_name="Detalle de Producto",
    )

    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del Producto",
    )

    descripcion = models.TextField(
        verbose_name="Descripción",
    )

    imagen = models.ImageField(
        upload_to="productos/",
        null=True,
        blank=True,
        verbose_name="Imagen",
    )

    estado = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Precio Base",
    )

    codigo_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
        null=True,
        blank=True,
        verbose_name="Categoría",
    )

    codigo_marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        related_name="productos",
        null=True,
        blank=True,
        verbose_name="Marca",
    )

    def save(self, *args, **kwargs):
<<<<<<< HEAD

        super().save(*args, **kwargs)

        if not self.codigo:
            self.codigo = f"PROD-{self.codigo_producto:05d}"

            super().save(
                update_fields=["codigo"]
            )
=======
        es_nuevo = self.pk is None
        if not self.codigo:
            ultimo = Producto.objects.order_by("-codigo_producto").first()
            siguiente_id = (ultimo.codigo_producto + 1) if ultimo else 1
            self.codigo = f"PROD-{siguiente_id:05d}"
        super().save(*args, **kwargs)
        if es_nuevo and self.codigo.startswith("PROD-"):
            codigo_real = f"PROD-{self.codigo_producto:05d}"
            if self.codigo != codigo_real:
                self.codigo = codigo_real
                super().save(update_fields=["codigo"])
>>>>>>> Valentina

    @property
    def stock_actual(self):

        if self.codigo_detalle_producto:
            return self.codigo_detalle_producto.cantidad_actual
<<<<<<< HEAD

        try:
            return self.detalle_producto.cantidad_actual
        except DetalleProducto.DoesNotExist:
            return 0

    @property
    def precio_venta_actual(self):

        adquisicion = (
            self.adquisiciones
            .order_by("-fecha", "-codigo")
            .first()
        )

=======
        return 0

    @property
    def precio_venta_actual(self):
        adquisicion = self.adquisiciones.order_by("-codigo_compra__fecha", "-codigo").first()
>>>>>>> Valentina
        if adquisicion:
            return adquisicion.precio_venta

        return self.precio

    @property
    def precio_compra_actual(self):
<<<<<<< HEAD

        adquisicion = (
            self.adquisiciones
            .order_by("-fecha", "-codigo")
            .first()
        )

=======
        adquisicion = self.adquisiciones.order_by("-codigo_compra__fecha", "-codigo").first()
>>>>>>> Valentina
        if adquisicion:
            return adquisicion.precio_compra

        return 0

    @property
    def precio_venta(self):
        return self.precio_venta_actual

    @classmethod
    def total_productos(cls):
        return cls.objects.count()

    @classmethod
    def total_activos(cls):
        return cls.objects.filter(
            estado=True
        ).count()

    @classmethod
    def total_inactivos(cls):
        return cls.objects.filter(
            estado=False
        ).count()

    def __str__(self):
        marca_str = f" ({self.codigo_marca.nombre})" if self.codigo_marca else ""
        return f"{self.codigo} - {self.nombre}{marca_str}"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


# ==========================================================
# 5. DETALLE PRODUCTO
# ==========================================================

class DetalleProducto(models.Model):
    codigo = models.AutoField(primary_key=True)
    cantidad_actual = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad Actual",
    )

    stock_min = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock Mínimo",
    )

    stock_max = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock Máximo",
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización",
    )

    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones",
    )

    @property
    def codigo_producto(self):
        return self.producto_principal.first()

    def __str__(self):
<<<<<<< HEAD

        if self.codigo_producto:
            return (
                f"{self.codigo_producto.nombre} "
                f"- Stock: {self.cantidad_actual}"
            )

=======
        prod = self.producto_principal.first()
        if prod:
            return f"{prod.nombre} - Stock: {self.cantidad_actual}"
>>>>>>> Valentina
        return f"Detalle Producto #{self.codigo}"

    class Meta:
        verbose_name = "Detalle de Producto"
        verbose_name_plural = "Detalles de Productos"


# ==========================================================
# 6. MOVIMIENTO DE PRODUCTO
# ==========================================================
class MovimientoProducto(models.Model):

    codigo = models.AutoField(
        primary_key=True
    )

    codigo_detalle_producto = models.ForeignKey(
        DetalleProducto,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="movimientos",
        verbose_name="Detalle de Producto"
    )

    TIPO_CHOICES = [
        ("entrada", "Entrada"),
        ("salida", "Salida"),
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Movimiento"
    )

    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad"
    )

    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha"
    )

    observacion = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Observación"
    )

    # ======================================================
    # PRODUCTO RELACIONADO
    # ======================================================

    @property
    def producto(self):
        if self.codigo_detalle_producto:
<<<<<<< HEAD
            return self.codigo_detalle_producto.codigo_producto
        return None

    # ======================================================
    # MOTIVO
    # ======================================================
=======
            return self.codigo_detalle_producto.producto_principal.first()
        return None
>>>>>>> Valentina

    @property
    def motivo(self):
        return self.observacion

    # ======================================================
    # REPRESENTACIÓN
    # ======================================================

    def __str__(self):
<<<<<<< HEAD

        if (
            self.codigo_detalle_producto
            and self.codigo_detalle_producto.codigo_producto
        ):
            producto = self.codigo_detalle_producto.codigo_producto

            return (
                f"{producto.codigo} - "
                f"{self.tipo} "
                f"{self.cantidad}"
            )

        return (
            f"Movimiento #{self.codigo} - "
            f"{self.tipo} "
            f"{self.cantidad}"
        )
=======
        prod = self.producto
        codigo_str = prod.codigo if prod else f"Detalle #{self.codigo_detalle_producto_id}"
        return f"{codigo_str} - {self.tipo} {self.cantidad}"
>>>>>>> Valentina

    class Meta:
        verbose_name = "Movimiento de Producto"
        verbose_name_plural = "Movimientos de Productos"


# ==========================================================
# 7. CREAR DETALLE AUTOMÁTICAMENTE
# ==========================================================

@receiver(post_save, sender=Producto)
<<<<<<< HEAD
def crear_detalle_producto(
    sender,
    instance,
    created,
    **kwargs
):

    if created:

        detalle_obj, creado = (
            DetalleProducto.objects.get_or_create(
                codigo_producto=instance,
                defaults={
                    "cantidad_actual": 0,
                    "stock_min": 0,
                    "stock_max": 0,
                },
            )
        )

        if not instance.codigo_detalle_producto_id:

            Producto.objects.filter(
                pk=instance.pk
            ).update(
                codigo_detalle_producto=detalle_obj
            )
=======
def crear_detalle_producto(sender, instance, created, **kwargs):
    if created and not instance.codigo_detalle_producto_id:
        detalle_obj = DetalleProducto.objects.create(
            cantidad_actual=0,
            stock_min=0,
            stock_max=0,
        )
        Producto.objects.filter(pk=instance.pk).update(
            codigo_detalle_producto=detalle_obj
        )
        instance.codigo_detalle_producto = detalle_obj
>>>>>>> Valentina


# ==========================================================
# 8. PROMOCIÓN
# ==========================================================

class Promocion(models.Model):

    codigo = models.AutoField(
        primary_key=True
    )

    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre",
    )

    porcentaje_descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Porcentaje de Descuento",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
    )

    fecha_inicio = models.DateField(
        verbose_name="Fecha de Inicio",
    )

    fecha_fin = models.DateField(
        verbose_name="Fecha de Fin",
    )

    imagen = models.ImageField(
        upload_to="promociones/",
        blank=True,
        null=True,
        verbose_name="Imagen",
    )

    estado = models.BooleanField(
        default=True,
        verbose_name="Estado",
    )

    codigo_producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promociones_directas",
        verbose_name="Producto Asociado",
    )

    codigo_servicio = models.ForeignKey(
        Servicios,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promociones_catalogo",
        verbose_name="Servicio Asociado",
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Promoción"
<<<<<<< HEAD
        verbose_name_plural = "Promociones"
=======
        verbose_name_plural = "Promociones"


# ==========================================================
# 9. SEÑAL DE AUDITORÍA AUTOMÁTICA EN BITÁCORA
# ==========================================================
@receiver(post_save, sender=MovimientoProducto)
def auditar_movimiento_inventario(sender, instance, created, **kwargs):
    if created:
        try:
            from historial.models import Bitacora
            tipo_str = "Entrada" if instance.tipo == "entrada" else "Salida"
            prod = instance.producto
            prod_nom = prod.nombre if prod else f"Detalle #{instance.codigo_detalle_producto_id}"
            obs = f" - {instance.observacion}" if instance.observacion else ""

            Bitacora.objects.create(
                codigo_detalle_producto=instance.codigo_detalle_producto,
                accion=f"{tipo_str} de Inventario",
                modulo="catalogo",
                descripcion=f"{tipo_str} de {instance.cantidad} unidad(es) de '{prod_nom}'{obs}.",
                ip_origen="127.0.0.1"
            )
        except Exception:
            pass

>>>>>>> Valentina

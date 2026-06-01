# facturas/models.py

from django.db import models
from usuarios.models import Usuario
from productos.models import Producto
from reservas.models import Reserva


# ==========================================
# FACTURA
# ==========================================

class Factura(models.Model):

    METODOS_PAGO = (
        ('efectivo', 'Efectivo'),
        ('nequi', 'Nequi'),
        ('daviplata', 'Daviplata'),
        ('tarjeta', 'Tarjeta'),
    )

    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('cancelada', 'Cancelada'),
    )

    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='facturas'
    )

    fecha_emision = models.DateTimeField(
        auto_now_add=True
    )

    total_pagado = models.FloatField(
        default=0
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente'
    )

    # Campos para clientes no registrados o para guardar el nombre/correo histórico
    nombre_cliente = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nombre del Cliente (si no es usuario registrado)"
    )
    correo_cliente = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Correo del Cliente (si no es usuario registrado)"
    )
    telefono_cliente = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Teléfono del Cliente (si no es usuario registrado)"
    )

    def __str__(self):
        return f"Factura #{self.id} - {self.cliente}"

class DetalleFactura(models.Model):

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detalle_factura'
    )

    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detalle_factura'
    )

    cantidad = models.IntegerField(
        default=1
    )

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.producto and not self.reserva:
            raise ValidationError('Un detalle de factura debe estar asociado a un producto o a una reserva.')
        if self.producto and self.reserva:
            raise ValidationError('Un detalle de factura no puede estar asociado a un producto y a una reserva simultáneamente.')

    def __str__(self):
        return f"Detalle Factura #{self.factura.id}"

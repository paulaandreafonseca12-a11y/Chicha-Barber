from decimal import Decimal

from django.test import TestCase

from usuarios.models import Usuario
from productos.models import Producto
from facturas.models import Factura, DetalleFactura


class FacturaTest(TestCase):
    def setUp(self):
        # Obtener datos existentes
        self.cliente = Usuario.objects.first()
        self.producto = Producto.objects.first()

    def test_crear_factura_y_detalles(self):
        # Verificar que existan datos
        self.assertIsNotNone(
            self.cliente,
            "No existe ningún usuario en la base de datos."
        )

        self.assertIsNotNone(
            self.producto,
            "No existe ningún producto en la base de datos."
        )

        # Crear factura
        factura = Factura.objects.create(
            cliente=self.cliente,
            metodo_pago="efectivo",
            estado="pendiente"
        )

        # Crear primer detalle
        detalle1 = DetalleFactura.objects.create(
            factura=factura,
            producto=self.producto,
            cantidad=2,
            precio_unitario=Decimal("15000.00")
        )

        # Crear segundo detalle
        detalle2 = DetalleFactura.objects.create(
            factura=factura,
            producto=self.producto,
            cantidad=3,
            precio_unitario=Decimal("10000.00")
        )

        # Actualizar datos desde la BD
        factura.refresh_from_db()

        # Mostrar resultados
        print("\n========== FACTURA ==========")
        print("ID:", factura.id)
        print("Cliente:", factura.cliente)
        print("Método de pago:", factura.metodo_pago)
        print("Estado:", factura.estado)
        print("Total pagado:", factura.total_pagado)

        print("\n========== DETALLES ==========")

        for detalle in factura.detalles.all():
            print("----------------------")
            print("Producto:", detalle.producto)
            print("Cantidad:", detalle.cantidad)
            print("Precio:", detalle.precio_unitario)
            print("Subtotal:", detalle.subtotal)

        # Validaciones
        self.assertEqual(detalle1.subtotal, Decimal("30000.00"))
        self.assertEqual(detalle2.subtotal, Decimal("30000.00"))
        self.assertEqual(factura.total_pagado, Decimal("60000.00"))

    def test_eliminar_detalle_actualiza_total(self):
        self.assertIsNotNone(self.cliente)
        self.assertIsNotNone(self.producto)

        factura = Factura.objects.create(
            cliente=self.cliente,
            metodo_pago="efectivo",
            estado="pendiente"
        )

        detalle = DetalleFactura.objects.create(
            factura=factura,
            producto=self.producto,
            cantidad=2,
            precio_unitario=Decimal("10000.00")
        )

        factura.refresh_from_db()
        self.assertEqual(factura.total_pagado, Decimal("20000.00"))

        # Eliminar detalle
        detalle.delete()

        factura.refresh_from_db()

        print("\nDetalle eliminado.")
        print("Nuevo total:", factura.total_pagado)

        self.assertEqual(factura.total_pagado, Decimal("0.00"))
from decimal import Decimal

from django.test import TestCase

from usuarios.models import Usuario
from productos.models import (
    Producto,
    Stock,
    Compra,
    DetalleCompra,
    MovimientoInventario
)


class ProductoCompraTest(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.first() or Usuario.objects.create_user(
            username='123456789',
            email='test_usuario@correo.com',
            password='Test1234*',
            first_name='Admin',
            last_name='User',
            telefono='3001234567',
            rol='admin'
        )

        self.producto = Producto.objects.create(
            nombre="Cerveza Poker",
            descripcion="Cerveza de prueba",
            precio_compra=Decimal("3000.00"),
            precio_venta=Decimal("5000.00"),
            estado=True
        )

        # El signal crea automáticamente el stock
        self.producto.refresh_from_db()

        self.producto.stock.cantidad = 20
        self.producto.stock.save()

    def test_crear_producto(self):

        print("\n========== PRODUCTO ==========")
        print("Código:", self.producto.codigo)
        print("Nombre:", self.producto.nombre)
        print("Precio Compra:", self.producto.precio_compra)
        print("Precio Venta:", self.producto.precio_venta)
        print("Stock:", self.producto.stock.cantidad)

        self.assertEqual(self.producto.stock.cantidad, 20)

    def test_crear_compra(self):

        compra = Compra.objects.create(
            usuario=self.usuario,
            nombre_cliente="Pedro",
            correo="pedro@gmail.com",
            telefono="3001234567",
            direccion="Bogotá",
            metodo_pago="persona",
            estado_pago="completado"
        )

        detalle = DetalleCompra.objects.create(
            compra=compra,
            producto=self.producto,
            cantidad=3
        )

        compra.actualizar_total()

        compra.refresh_from_db()
        self.producto.stock.refresh_from_db()

        print("\n========== COMPRA ==========")
        print("Compra:", compra.codigo_compra)
        print("Cliente:", compra.nombre_cliente)
        print("Total:", compra.total)

        print("\n========== DETALLE ==========")
        print("Producto:", detalle.producto.nombre)
        print("Cantidad:", detalle.cantidad)
        print("Subtotal:", detalle.subtotal)

        print("\n========== STOCK ==========")
        print("Stock restante:", self.producto.stock.cantidad)

        self.assertEqual(detalle.subtotal, Decimal("15000.00"))
        self.assertEqual(compra.total, Decimal("15000.00"))
        self.assertEqual(self.producto.stock.cantidad, 17)

    def test_movimiento_inventario(self):

        compra = Compra.objects.create(
            usuario=self.usuario,
            nombre_cliente="Pedro",
            metodo_pago="persona",
            estado_pago="completado"
        )

        DetalleCompra.objects.create(
            compra=compra,
            producto=self.producto,
            cantidad=2
        )

        movimiento = MovimientoInventario.objects.last()

        print("\n========== MOVIMIENTO ==========")
        print("Producto:", movimiento.producto.nombre)
        print("Tipo:", movimiento.tipo)
        print("Cantidad:", movimiento.cantidad)
        print("Motivo:", movimiento.motivo)

        self.assertEqual(movimiento.tipo, "salida")
        self.assertEqual(movimiento.cantidad, 2)

    def test_stock_insuficiente(self):

        compra = Compra.objects.create(
            usuario=self.usuario,
            nombre_cliente="Pedro",
            metodo_pago="persona",
            estado_pago="completado"
        )

        with self.assertRaises(ValueError):

            DetalleCompra.objects.create(
                compra=compra,
                producto=self.producto,
                cantidad=100
            )

        print("\n[OK] Se detectó correctamente el stock insuficiente.")

# Create your tests here.

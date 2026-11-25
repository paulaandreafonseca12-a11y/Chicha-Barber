from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from catalogo.models import Proveedor, Categoria, Marca, Producto, DetalleProducto, MovimientoProducto
from compra.models import Compra, DetalleCompra
from usuarios.models import RolUsuario, Usuario


class CompraModelTestCase(TestCase):
    """Pruebas QA para Compras, cálculo de subtotales e incremento de stock."""

    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            nombre="Distribuidora Barber Test",
            telefono="3001234567",
            correo="proveedor@test.com",
            direccion="Calle 1 # 2-3"
        )
        self.categoria = Categoria.objects.create(
            nombre="Navajas y Cuchillas",
            descripcion="Insumos de afeitado"
        )
        self.marca = Marca.objects.create(
            nombre="SharpEdge",
            descripcion="Marca de hojas"
        )
        self.detalle_prod = DetalleProducto.objects.create(
            cantidad_actual=10,
            stock_min=5,
            stock_max=100
        )
        self.producto = Producto.objects.create(
            codigo_categoria=self.categoria,
            codigo_marca=self.marca,
            codigo_detalle_producto=self.detalle_prod,
            nombre="Caja Hojas de Afeitar",
            descripcion="Caja por 100 unidades",
            precio=Decimal("15000.00"),
            estado=True
        )

    def test_crear_compra_actualiza_total_e_inventario(self):
        """Verifica que crear un detalle de compra aumente stock y recalcule total."""
        compra = Compra.objects.create(
            codigo_proveedor=self.proveedor,
            observaciones="Compra de reposición mensual"
        )
        self.assertIn("Distribuidora Barber Test", str(compra))
        self.assertEqual(compra.total, Decimal("0.00"))

        detalle = DetalleCompra.objects.create(
            codigo_compra=compra,
            codigo_producto=self.producto,
            cantidad=20,
            precio_compra=Decimal("8000.00"),
            precio_venta=Decimal("15000.00")
        )

        # 1. Verifica subtotal
        self.assertEqual(detalle.subtotal, Decimal("160000.00"))

        # 2. Verifica total en compra
        compra.refresh_from_db()
        self.assertEqual(compra.total, Decimal("160000.00"))

        # 3. Verifica aumento de stock en catálogo
        self.detalle_prod.refresh_from_db()
        self.assertEqual(self.detalle_prod.cantidad_actual, 30)

        # 4. Verifica creación de movimiento de entrada
        movimiento = detalle.codigo_movimiento_producto
        self.assertIsNotNone(movimiento)
        self.assertEqual(movimiento.tipo, "entrada")
        self.assertEqual(movimiento.cantidad, 20)


class CompraAdminAccessTests(TestCase):
    def test_cliente_no_puede_abrir_gestion_de_compras(self):
        cliente = Usuario.objects.create_user(
            email='cliente-compras@example.com',
            password='test-password',
            primer_nombre='Cliente',
            primer_apellido='Prueba',
            telefono='3000000002',
            numero_documento='990000002',
            rol=RolUsuario.CLIENTE,
        )
        self.client.force_login(cliente)

        response = self.client.get(reverse('lista_adquisiciones'))

        self.assertEqual(response.status_code, 403)

    def test_administrador_puede_abrir_gestion_de_compras(self):
        administrador = Usuario.objects.create_user(
            email='admin-compras@example.com',
            password='test-password',
            primer_nombre='Admin',
            primer_apellido='Prueba',
            telefono='3000000004',
            numero_documento='990000004',
            rol=RolUsuario.ADMIN,
        )
        self.client.force_login(administrador)

        response = self.client.get(reverse('lista_adquisiciones'))

        self.assertEqual(response.status_code, 200)


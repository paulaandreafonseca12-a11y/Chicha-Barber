from django.test import TestCase

from datetime import date, time
from decimal import Decimal

from django.utils import timezone

from usuarios.models import Usuario, Notificacion
from servicios.models import Servicios
from reservas.models import Turno, Reserva
class TurnoModelTest(TestCase):

    def setUp(self):
        self.barbero = Usuario.objects.create(
            username="barbero1",
            first_name="Juan",
            last_name="Pérez",
            rol="barbero"
        )

    def test_crear_turno(self):
        turno = Turno.objects.create(
            profesional=self.barbero,
            fecha=date.today(),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            estado="disponible"
        )

        self.assertEqual(turno.profesional, self.barbero)
        self.assertEqual(turno.estado, "disponible")

    def test_str_turno(self):
        turno = Turno.objects.create(
            profesional=self.barbero,
            fecha=date.today(),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0)
        )

        texto = str(turno)

        self.assertIn("Juan", texto)
        self.assertIn("09:00:00", texto)


class ReservaModelTest(TestCase):

    def setUp(self):

        self.barbero = Usuario.objects.create(
            username="barbero",
            first_name="Carlos",
            last_name="Ramírez",
            rol="barbero"
        )

        self.cliente = Usuario.objects.create(
            username="cliente",
            first_name="Pedro",
            last_name="López",
            rol="cliente"
        )

        self.admin = Usuario.objects.create(
            username="admin",
            first_name="Administrador",
            last_name="Sistema",
            rol="admin"
        )

        self.servicio = Servicios.objects.create(
            nombre="Corte clásico",
            precio=Decimal("25000")
        )

        self.turno = Turno.objects.create(
            profesional=self.barbero,
            fecha=date.today(),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0)
        )

    def test_crear_reserva(self):

        reserva = Reserva.objects.create(
            turno=self.turno,
            cliente=self.cliente,
            servicio=self.servicio,
            precio_historico=Decimal("25000")
        )

        self.assertEqual(reserva.cliente, self.cliente)
        self.assertEqual(reserva.estado, "reservada")
        self.assertEqual(reserva.servicio, self.servicio)

    def test_fecha_reserva_automatica(self):

        reserva = Reserva.objects.create(
            turno=self.turno,
            cliente=self.cliente,
            servicio=self.servicio
        )

        self.assertIsNotNone(reserva.fecha_reserva)

        fecha_esperada = timezone.make_aware(
            timezone.datetime.combine(
                self.turno.fecha,
                self.turno.hora_inicio
            )
        )

        self.assertEqual(reserva.fecha_reserva, fecha_esperada)

    def test_str_reserva(self):

        reserva = Reserva.objects.create(
            turno=self.turno,
            cliente=self.cliente,
            servicio=self.servicio
        )

        texto = str(reserva)

        self.assertIn("Pedro", texto)
        self.assertIn("Corte clásico", texto)

    def test_notificacion_cliente(self):

        Reserva.objects.create(
            turno=self.turno,
            cliente=self.cliente,
            servicio=self.servicio
        )

        self.assertTrue(
            Notificacion.objects.filter(
                usuario=self.cliente,
                tipo="reserva"
            ).exists()
        )

    def test_notificacion_admin(self):

        Reserva.objects.create(
            turno=self.turno,
            cliente=self.cliente,
            servicio=self.servicio
        )

        self.assertTrue(
            Notificacion.objects.filter(
                usuario=self.admin,
                tipo="reserva"
            ).exists()
        )

    def test_reserva_sin_cliente_registrado(self):

        reserva = Reserva.objects.create(
            turno=self.turno,
            nombre_cliente="Cliente Invitado",
            correo_cliente="cliente@test.com",
            telefono_cliente="3000000000",
            servicio=self.servicio
        )

        self.assertEqual(reserva.nombre_cliente, "Cliente Invitado")

    def test_estado_por_defecto(self):

        reserva = Reserva.objects.create(
            turno=self.turno,
            cliente=self.cliente,
            servicio=self.servicio
        )

        self.assertEqual(reserva.estado, "reservada")

    def test_precio_historico(self):

        reserva = Reserva.objects.create(
            turno=self.turno,
            cliente=self.cliente,
            servicio=self.servicio,
            precio_historico=Decimal("30000")
        )

        self.assertEqual(
            reserva.precio_historico,
            Decimal("30000")
        )
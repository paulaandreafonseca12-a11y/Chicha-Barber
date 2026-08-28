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
            email="barbero1@example.com",
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
            email="barbero@example.com",
            first_name="Carlos",
            last_name="Ramírez",
            rol="barbero"
        )

        self.usuario = Usuario.objects.create(
            username="cliente",
            email="cliente@example.com",
            first_name="Pedro",
            last_name="López",
            rol="cliente"
        )

        self.admin = Usuario.objects.create(
            username="admin",
            email="admin@example.com",
            first_name="Administrador",
            last_name="Sistema",
            rol="admin"
        )

        self.servicio = Servicios.objects.create(
            nombre="Corte clásico",
            precio=Decimal("25000"),
            duracion=30,
            descripcion="Corte clásico de prueba"
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
            usuario=self.usuario,
            servicio=self.servicio,
            precio_historico=Decimal("25000")
        )

        self.assertEqual(reserva.usuario, self.usuario)
        self.assertEqual(reserva.estado, "reservada")
        self.assertEqual(reserva.servicio, self.servicio)

    def test_fecha_reserva_automatica(self):

        reserva = Reserva.objects.create(
            turno=self.turno,
            usuario=self.usuario,
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
            usuario=self.usuario,
            servicio=self.servicio
        )

        texto = str(reserva)

        self.assertIn("Pedro", texto)
        self.assertIn("Corte clásico", texto)

    def test_notificacion_usuario(self):

        Reserva.objects.create(
            turno=self.turno,
            usuario=self.usuario,
            servicio=self.servicio
        )

        self.assertTrue(
            Notificacion.objects.filter(
                usuario=self.usuario,
                tipo="reserva"
            ).exists()
        )

    def test_notificacion_admin(self):

        Reserva.objects.create(
            turno=self.turno,
            usuario=self.usuario,
            servicio=self.servicio
        )

        self.assertTrue(
            Notificacion.objects.filter(
                usuario=self.admin,
                tipo="reserva"
            ).exists()
        )

    def test_reserva_sin_usuario_registrado(self):

        reserva = Reserva.objects.create(
            turno=self.turno,
            nombre_usuario="Cliente Invitado",
            correo_usuario="cliente@test.com",
            telefono_usuario="3000000000",
            servicio=self.servicio
        )

        self.assertEqual(reserva.nombre_usuario, "Cliente Invitado")

    def test_estado_por_defecto(self):

        reserva = Reserva.objects.create(
            turno=self.turno,
            usuario=self.usuario,
            servicio=self.servicio
        )

        self.assertEqual(reserva.estado, "reservada")

    def test_precio_historico(self):

        reserva = Reserva.objects.create(
            turno=self.turno,
            usuario=self.usuario,
            servicio=self.servicio,
            precio_historico=Decimal("30000")
        )

        self.assertEqual(
            reserva.precio_historico,
            Decimal("30000")
        )
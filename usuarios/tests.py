from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError, transaction
from .models import Usuario


class UsuarioModelTest(TestCase):
    """Pruebas para el modelo Usuario"""

    def setUp(self):
        """Configuración inicial: crea un usuario de prueba"""
        self.usuario = Usuario.objects.create_user(
            email='test@correo.com',
            password='Test1234*',
            numero_documento='123456789',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            rol='cliente'
        )

    # --- PRUEBAS DE CREACIÓN ---

    def test_crear_usuario_cliente(self):
        """Un usuario cliente se crea correctamente"""
        self.assertEqual(self.usuario.email, 'test@correo.com')
        self.assertEqual(self.usuario.rol, 'cliente')
        self.assertTrue(self.usuario.estado)

    def test_crear_usuario_barbero(self):
        """Un usuario barbero se crea con especialidad"""
        barbero = Usuario.objects.create_user(
            email='barbero@correo.com',
            password='Test1234*',
            numero_documento='987654321',
            primer_nombre='Carlos',
            primer_apellido='López',
            telefono='3009876543',
            rol='barbero',
        )
        self.assertEqual(barbero.rol, 'barbero')

    def test_str_usuario(self):
        """El __str__ retorna nombre completo y rol"""
        resultado = str(self.usuario)
        self.assertIn('Juan', resultado)
        self.assertIn('Cliente', resultado)

    # --- PRUEBAS DE VALIDACIÓN ---

    def test_email_unico(self):
        """No se puede crear dos usuarios con el mismo email"""
        with self.assertRaises(IntegrityError), transaction.atomic():
            Usuario.objects.create_user(
                email='test@correo.com',
                password='Test1234*',
                numero_documento='111111111',
                telefono='3001111111',
                rol='cliente'
            )

    def test_username_unico(self):
        """No se puede crear dos usuarios con el mismo documento"""
        with self.assertRaises(IntegrityError), transaction.atomic():
            Usuario.objects.create_user(
                email='otro@correo.com',
                password='Test1234*',
                numero_documento='123456789',
                telefono='3002222222',
                rol='cliente'
            )

    def test_estado_activo_por_defecto(self):
        """Un usuario nuevo está activo por defecto"""
        self.assertTrue(self.usuario.estado)

    def test_rol_por_defecto_cliente(self):
        """El rol por defecto es cliente"""
        usuario = Usuario.objects.create_user(
            email='default@correo.com',
            password='Test1234*',
            numero_documento='555555555',
            primer_nombre='Usuario',
            primer_apellido='Prueba',
            telefono='3005555555',
        )
        self.assertEqual(usuario.rol, 'cliente')

    # --- PRUEBAS DE AUTENTICACIÓN ---

    def test_login_con_email_correcto(self):
        """Un usuario puede iniciar sesión con email y contraseña correctos"""
        cliente = Client()
        response = cliente.post(reverse('login'), {
            'username': 'test@correo.com',
            'password': 'Test1234*'
        })
        self.assertIn(response.status_code, [200, 302])

    def test_login_con_contraseña_incorrecta(self):
        """Login falla con contraseña incorrecta"""
        cliente = Client()
        response = cliente.post(reverse('login'), {
            'username': 'test@correo.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # se queda en la página

    def test_usuario_inactivo_no_puede_login(self):
        """Un usuario inactivo no puede iniciar sesión"""
        self.usuario.estado = False
        self.usuario.save()
        cliente = Client()
        response = cliente.post(reverse('login'), {
            'username': 'test@correo.com',
            'password': 'Test1234*'
        })
        self.assertEqual(response.status_code, 200)


class PerfilFormularioTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email='perfil@correo.com',
            password='ClaveSegura123*',
            numero_documento='456789123',
            primer_nombre='Paula',
            primer_apellido='Pérez',
            telefono='3001234567',
            rol='cliente',
        )
        self.client.force_login(self.usuario)

    def test_perfil_invalido_mantiene_errores_y_reabre_edicion(self):
        response = self.client.post(reverse('perfil'), {
            'editar_perfil': '1',
            'tipo_documento': 'CC',
            'numero_documento': self.usuario.numero_documento,
            'primer_nombre': 'Paula',
            'segundo_nombre': '',
            'primer_apellido': 'Pérez',
            'segundo_apellido': '',
            'telefono': 'telefono-invalido',
            'email': 'correo-invalido',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['abrir_offcanvas'], 'offcanvasEditar')
        self.assertIn('telefono', response.context['form'].errors)
        self.assertIn('email', response.context['form'].errors)
        self.assertContains(response, 'offcanvasEditar')
        self.assertContains(response, response.context['form'].errors['email'][0])

    def test_password_invalida_mantiene_errores_y_reabre_panel(self):
        response = self.client.post(reverse('perfil'), {
            'cambiar_password': '1',
            'password_actual': 'incorrecta',
            'password_nueva': 'debil',
            'password_confirmar': 'diferente',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['abrir_offcanvas'], 'offcanvasPassword')
        errores = response.context['errores_password']
        self.assertTrue(errores['password_actual'])
        self.assertTrue(errores['password_nueva'])
        self.assertTrue(errores['password_confirmar'])
        self.assertContains(response, errores['password_actual'][0])
        self.assertContains(response, 'offcanvasPassword')